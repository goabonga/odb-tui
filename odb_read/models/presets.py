"""Tire and gearbox presets for gear estimation."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class TirePreset:
    """Dimension pneu et circonférence associée.

    Attributes:
        label: Désignation du pneu (ex. '205/55R16').
        circumference: Circonférence de roulement en mètres.
    """

    label: str
    circumference: float  # meters


@dataclass
class GearboxPreset:
    """Configuration boîte de vitesses pour l'estimation du rapport engagé.

    Attributes:
        label: Nom descriptif (ex. '6 vitesses').
        nb_gears: Nombre de rapports.
        final_drive: Rapport de pont (réduction finale).
        ratios: Rapport de démultiplication par vitesse {numéro: ratio}.
    """

    label: str
    nb_gears: int
    final_drive: float
    ratios: Dict[int, float]


# Préréglages pneus courants (dimensions européennes fréquentes)
TIRE_PRESETS = [
    TirePreset("195/65R15", 1.996),
    TirePreset("205/55R16", 1.976),
    TirePreset("205/60R16", 2.041),
    TirePreset("215/55R16", 2.011),
    TirePreset("215/60R17", 2.167),
    TirePreset("215/65R16", 2.108),
    TirePreset("225/45R17", 1.961),
    TirePreset("225/50R17", 2.042),
    TirePreset("225/55R17", 2.106),
    TirePreset("225/65R17", 2.268),
    TirePreset("235/55R18", 2.193),
    TirePreset("235/60R18", 2.258),
    TirePreset("245/45R18", 2.079),
    TirePreset("255/55R19", 2.303),
]

DEFAULT_TIRE_INDEX = 4  # 215/60R17

# Préréglages boîtes de vitesses (rapports typiques diesel/essence)
GEARBOX_PRESETS = [
    GearboxPreset("5 vitesses", 5, 3.938, {
        1: 3.583, 2: 1.952, 3: 1.281, 4: 0.951, 5: 0.757,
    }),
    GearboxPreset("6 vitesses", 6, 3.700, {
        1: 3.727, 2: 2.048, 3: 1.393, 4: 1.000, 5: 0.807, 6: 0.637,
    }),
    GearboxPreset("4 vitesses", 4, 3.730, {
        1: 3.587, 2: 2.022, 3: 1.351, 4: 1.000,
    }),
]

DEFAULT_GEARBOX_INDEX = 0  # 5 vitesses
