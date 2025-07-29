import logging
import os
import shutil
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

import hydra
import torch
from hydra.utils import instantiate
from lightning.pytorch import seed_everything
from meds import held_out_split, train_split, tuning_split
from meds_torchdata import MEDSTorchDataConfig
from MEDS_transforms.runner import load_yaml_file
from omegaconf import DictConfig, OmegaConf

from .generation import format_trajectories, get_timeline_end_token_idx
from .training import MEICARModule, find_checkpoint_path, validate_resume_directory

# Import OmegaConf Resolvers
from .utils import (
    gpus_available,
    hash_based_seed,
    int_prod,
    is_mlflow_logger,
    num_cores,
    num_gpus,
    oc_min,
    resolve_generation_context_size,
    save_resolved_config,
    sub,
)

logger = logging.getLogger(__name__)

CONFIGS = files("MEDS_EIC_AR") / "configs"

MEDSTorchDataConfig.add_to_config_store("datamodule/config")


@hydra.main(version_base=None, config_path=str(CONFIGS), config_name="_pretrain")
def pretrain(cfg: DictConfig):
    st = datetime.now(tz=UTC)

    if cfg.do_overwrite and cfg.do_resume:
        logger.warning(
            "Both `do_overwrite` and `do_resume` are set to True. "
            "Only `do_overwrite` will be used, and the output directory will be cleared."
        )

    output_dir = Path(cfg.output_dir)

    if output_dir.is_file():
        raise NotADirectoryError(f"Output directory {output_dir} is a file, not a directory.")

    cfg_path = output_dir / "config.yaml"

    ckpt_path = None

    if cfg_path.exists():
        if cfg.do_overwrite:
            logger.info(f"Overwriting existing output directory {output_dir}.")
            shutil.rmtree(output_dir, ignore_errors=True)
        elif cfg.do_resume:
            validate_resume_directory(output_dir, cfg)
            ckpt_path = find_checkpoint_path(output_dir)
        else:
            raise FileExistsError(
                f"Output directory {output_dir} already exists and is populated. "
                "Use `do_overwrite` or `do_resume` to proceed."
            )
    else:
        OmegaConf.save(cfg, output_dir / "config.yaml")
        save_resolved_config(cfg, output_dir / "resolved_config.yaml")

    logger.info("Setting torch float32 matmul precision to 'medium'.")
    torch.set_float32_matmul_precision("medium")

    D = instantiate(cfg.datamodule)

    gpt_kwargs = {"vocab_size": D.config.vocab_size, "eos_token_id": get_timeline_end_token_idx(D.config)}

    M = instantiate(
        cfg.lightning_module,
        model={"gpt_kwargs": gpt_kwargs},
        metrics={"vocab_size": D.config.vocab_size},
    )

    if M.model.do_demo or cfg.get("seed", None):
        seed_everything(cfg.get("seed", 1), workers=True)

    trainer = instantiate(cfg.trainer)
    if any(is_mlflow_logger(logger) for logger in trainer.loggers):
        # We do the import only here to avoid importing mlflow if it isn't installed.
        import mlflow

        if "MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING" not in os.environ:
            # The user can set this environment variable to enable or disable system metrics logging on their
            # own, but if they don't, it will by default be enabled.
            mlflow.enable_system_metrics_logging()

    trainer_kwargs = {"model": M, "datamodule": D}
    if ckpt_path:
        logger.info(f"Trying to resume training from checkpoint {ckpt_path}.")
        trainer_kwargs["ckpt_path"] = ckpt_path

    trainer.fit(**trainer_kwargs)

    best_ckpt_path = Path(trainer.checkpoint_callback.best_model_path)
    if not best_ckpt_path.is_file():
        raise ValueError("No best checkpoint reported.")

    output_fp = Path(cfg.output_dir) / "best_model.ckpt"
    shutil.copyfile(best_ckpt_path, output_fp)

    best_score = trainer.checkpoint_callback.best_model_score

    logger.info(f"Best checkpoint (with score {best_score:.2f}) copied to {output_fp!s}.")
    logger.info(f"Training complete in {datetime.now(tz=UTC) - st}")


@hydra.main(version_base=None, config_path=str(CONFIGS), config_name="_generate_trajectories")
def generate_trajectories(cfg: DictConfig):
    st = datetime.now(tz=UTC)

    logger.info("Setting torch float32 matmul precision to 'medium'.")
    torch.set_float32_matmul_precision("medium")

    D = instantiate(cfg.datamodule)

    M = MEICARModule.load_from_checkpoint(Path(cfg.ckpt_path))
    M.eval()

    trainer = instantiate(cfg.trainer)

    inference = cfg.inference

    if cfg.get("seed", None):
        seed_everything(cfg.get("seed", 1), workers=True)

    for split in inference.generate_for_splits:
        if split == train_split:
            dataloader = D.train_dataloader()
        elif split == tuning_split:
            dataloader = D.val_dataloader()
        elif split == held_out_split:
            dataloader = D.test_dataloader()
        else:
            raise ValueError(f"Unknown split {split}.")

        for sample in range(inference.N_trajectories_per_task_sample):
            out_fp = Path(cfg.output_dir) / split / f"{sample}.parquet"
            out_fp.parent.mkdir(parents=True, exist_ok=True)

            if out_fp.is_file() and not cfg.do_overwrite:
                logger.info(f"Skipping {out_fp} as it already exists.")
                continue
            else:
                out_fp.parent.mkdir(parents=True, exist_ok=True)

            seed = hash_based_seed(cfg.get("seed", None), split, sample)

            logger.info(f"Generating trajectories for {split} sample {sample} to {out_fp} with seed {seed}.")

            seed_everything(seed, workers=True)
            predictions = trainer.predict(model=M, dataloaders=dataloader)
            predictions_df = format_trajectories(dataloader.dataset, predictions)
            predictions_df.write_parquet(out_fp, use_pyarrow=True)

    logger.info(f"Generation of trajectories complete in {datetime.now(tz=UTC) - st}")
