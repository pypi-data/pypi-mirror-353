import hydra
from omegaconf import DictConfig, OmegaConf

from chem_mrl.schemas import (
    BaseConfig,
    ChemMRLConfig,
    register_chem_mrl_configs,
)
from chem_mrl.trainers import ChemMRLTrainer

register_chem_mrl_configs()


@hydra.main(
    config_path="../chem_mrl/conf",
    config_name="chem_mrl_config",
    version_base="1.2",
)
def main(_cfg: DictConfig):
    cfg = OmegaConf.to_object(_cfg)
    assert isinstance(cfg, BaseConfig)
    assert isinstance(cfg.model, ChemMRLConfig)
    trainer = ChemMRLTrainer(cfg)
    trainer.train()


if __name__ == "__main__":
    main()
