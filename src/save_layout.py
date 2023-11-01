from functools import cached_property, reduce
import itertools
import math
import time

from typing import Dict, List, Optional
import pandas

from pydantic import BaseModel, Field


class Hepteract(BaseModel, alias_generator=lambda s: s.upper()):
    """Single Hepteract"""

    balance: float = Field(alias="BAL")
    cap: float
    base_cap: float
    hepteract_conversion: int

    @property
    def tier(self) -> int:
        """Return the tier of the hepteract."""
        return int(math.log2(self.cap / self.base_cap) + 1)

    @property
    def level_cost(self) -> int:
        hepts = int(self.cap * self.hepteract_conversion)
        return hepts

    @property
    def next_level_cost(self) -> int:
        hepts = int(self.cap * 2 * self.hepteract_conversion)
        return hepts

    @property
    def to_level(self) -> int:
        if self.level_cost - int(self.balance * self.hepteract_conversion) == 0:
            return self.next_level_cost

        return self.level_cost - int(self.balance * self.hepteract_conversion)

    def _total_cost_counter(self, tier: int) -> int:
        if tier == 1:
            return self.level_cost

        return self._total_cost_counter(tier - 1) + self.level_cost

    @cached_property
    def total_cost(self) -> int:
        return self._total_cost_counter(self.tier)

    def effective_boost(self, limit: float, dr: float, boost: float) -> float:
        if self.balance < limit:
            return self.balance
        return limit * (self.balance / limit) ** (dr + boost)


class HepteractCrafts(BaseModel):
    """Class for hepteract types"""

    chronos: Hepteract
    hyperrealism: Hepteract
    quark: Hepteract
    challenge: Hepteract
    abyss: Hepteract
    accelerator: Hepteract
    acceleratorBoost: Hepteract
    multiplier: Hepteract


class ShopUpgrades(BaseModel):
    """Quark shop upgrades"""

    offeringPotion: int
    obtainiumPotion: int
    offeringEX: int
    offeringAuto: int
    obtainiumEX: int
    obtainiumAuto: int
    instantChallenge: int
    antSpeed: int
    cashGrab: int
    shopTalisman: int
    seasonPass: int
    challengeExtension: int
    challengeTome: int
    cubeToQuark: int
    tesseractToQuark: int
    hypercubeToQuark: int
    seasonPass2: int
    seasonPass3: int
    chronometer: int
    infiniteAscent: int
    calculator: int
    calculator2: int
    calculator3: int
    calculator4: int
    calculator5: int
    calculator6: int
    constantEX: int
    powderEX: int
    chronometer2: int
    chronometer3: int
    seasonPassY: int
    seasonPassZ: int
    challengeTome2: int
    instantChallenge2: int
    cashGrab2: int
    chronometerZ: int
    cubeToQuarkAll: int
    offeringEX2: int
    obtainiumEX2: int
    seasonPassLost: int
    powderAuto: int
    challenge15Auto: int
    extraWarp: int
    autoWarp: int
    improveQuarkHept: int
    improveQuarkHept2: int
    improveQuarkHept3: int
    improveQuarkHept4: int
    shopImprovedDaily: int
    shopImprovedDaily2: int
    shopImprovedDaily3: int
    shopImprovedDaily4: int
    offeringEX3: int
    obtainiumEX3: int
    improveQuarkHept5: int
    seasonPassInfinity: int
    chronometerInfinity: int
    shopSingularityPenaltyDebuff: int
    shopAmbrosiaGeneration1: int
    shopAmbrosiaGeneration2: int
    shopAmbrosiaGeneration3: int
    shopAmbrosiaGeneration4: int
    shopAmbrosiaLuck1: int
    shopAmbrosiaLuck2: int
    shopAmbrosiaLuck3: int
    shopAmbrosiaLuck4: int


class QuarkCost(BaseModel):
    base: int
    inc: int

    def quark_cost(self, level: int) -> int:
        return math.floor(((self.base + self.inc * level) * level) / 2)


class ShopQuarkCosts(BaseModel):
    seasonPass: QuarkCost
    seasonPass2: QuarkCost
    seasonPass3: QuarkCost
    seasonPassY: QuarkCost
    chronometer: QuarkCost
    chronometer2: QuarkCost
    offeringEX: QuarkCost
    offeringAuto: QuarkCost
    obtainiumEX: QuarkCost
    obtainiumAuto: QuarkCost
    antSpeed: QuarkCost
    cashGrab: QuarkCost


class ShopBuys:
    accel1: int
    accel2: int
    accelCost: int
    wow3: int
    wowY: int
    wowCost: int

    def __init__(self, sd: pandas.DataFrame, quarks: int) -> None:
        wow_pass_idx: int = (sd["WoW Passes"][sd["WoW Passes", "Cost"] - quarks < 0]).idxmax()["Cost"]  # type: ignore[index, assignment]
        accel_idx: int = (sd["Acceleration"][sd["Acceleration", "Cost"] - quarks < 0]).idxmax()["Cost"]  # type: ignore[index, assignment]

        self.wow3, self.wowY, self.wowCost = [int(x) for x in sd["WoW Passes"].iloc[wow_pass_idx].tolist()]
        self.accel1, self.accel2, self.accelCost = [int(x) for x in sd["Acceleration"].iloc[accel_idx].tolist()]


class SynergismConfig(BaseModel):
    targetGainPercent: int
    addUsesPerDay: int
    hps: float
    shopQuarkCost: ShopQuarkCosts


class SynergismGame(BaseModel):
    """A Synergise savegame. All ints are floats due to scinetific notation."""

    wowCubes: float
    wowTesseracts: float
    wowHypercubes: float
    wowPlatonicCubes: float
    wowAbyssals: float
    singularityCount: float
    challenge15Exponent: float
    quarksLeft: float = Field(alias="worlds")
    overfluxPowder: float
    overfluxOrbs: float
    shop: ShopUpgrades = Field(alias="shopUpgrades")
    hepts: HepteractCrafts = Field(alias="hepteractCrafts")
    platonicUpgrades: List[int]
    usedCorruptions: List[int]
    achievements: List[int]
    ascensionCount: int
    ascensionCounter: float
    saveTime: int = Field(alias="offlinetick")

    config: Optional[SynergismConfig] = Field(skip=True, required=False, default=None)

    shop_benefit_hept: float = Field(skip=True, required=False, default=0)
    shop_benefit_accel: float = Field(skip=True, required=False, default=0)

    def set_config(self, config: SynergismConfig) -> None:
        self.config = config

    def set_shop_benefits(self, buys: ShopBuys) -> None:
        if self.total_quarks > 2000:
            self.shop_benefit_accel = round(1 + 0.01 * buys.accel1 + buys.accel2 * 0.005 + 0.01 * buys.accel1 * buys.accel2 * 0.005, 3)
        
        if self.total_quarks > 5000:
            self.shop_benefit_hept = round(1 +  0.01 * buys.wow3 + buys.wowY * 0.005 + 0.01 * buys.wow3 * buys.wowY * 0.005, 3)

    def get_plat_upgrade(self, row: int, column: int) -> int:
        try:
            return self.platonicUpgrades[(row - 1) * 5 + column]
        except IndexError:
            return 0

    def get_achievement(self, id: int) -> int:
        try:
            return self.achievements[id]
        except IndexError:
            return 0

    @property
    def u44(self) -> int:
        return self.get_plat_upgrade(4, 4)

    @cached_property
    def chronos_percent(self) -> float:
        return (1000 * ((self.hepts.chronos.balance / 1000) ** ((1 / 6) + ((1 / 750) * self.u44)))) * (6 / 100)

    @cached_property
    def chronos_percent_next(self) -> float:
        return (1000 * ((2 ** (self.hepts.chronos.tier)) ** ((1 / 6) + ((1 / 750) * self.u44)))) * (6 / 100)

    @cached_property
    def chronos_increase(self) -> float:
        return ((self.chronos_percent_next + 100) / (self.chronos_percent + 100) - 1) * 100

    @cached_property
    def multiplier(self) -> float:
        c15boost: float = (
            1 + 0.05 + 2 * math.log2(self.challenge15Exponent / 1.5e18) / 100
            if (self.challenge15Exponent > 1.5e18)
            else 1
        )
        shopUpgrades: float = (
            (1 + self.shop.chronometer / 100)
            * (1 + 0.5 * self.shop.chronometer2 / 100)
            * (1 + 1.5 * self.shop.chronometer3 / 100)
        )
        omegaBoost = 1 + 0.002 * sum(self.usedCorruptions) * self.get_plat_upgrade(3, 5)
        chronosBoost = 1 + 0.6 / 1000 * self.hepts.chronos.effective_boost(1000, 1 / 6, 1 / 750 * self.u44)
        achievementBoost = (1 + min(0.1, 1 / 100 * math.log10(self.ascensionCount + 1)) * self.get_achievement(262)) * (
            1 + min(0.10, 1 / 100 * math.log10(self.ascensionCount + 1)) * self.get_achievement(263)
        )

        return c15boost * shopUpgrades * omegaBoost * chronosBoost * achievementBoost

    @property
    def current_ascension_timer(self) -> float:
        now = int(time.time() * 1000)
        return ((now - self.saveTime) / 1000) * self.multiplier + self.ascensionCounter

    @cached_property
    def total_quarks(self) -> int:
        if self.config is None:
            raise ValueError("Config not set")

        used_sum = 0
        for item in self.config.shopQuarkCost.model_fields.keys():
            level = getattr(self.shop, item)
            if item.endswith("Auto"):
                level -= 1
            used_sum += getattr(self.config.shopQuarkCost, item).quark_cost(level)

        return math.floor(self.quarksLeft) + used_sum - 15

    @cached_property
    def hept_per_day(self) -> float:
        if not self.config:
            raise ValueError("Config not set")

        return self.shop_benefit_hept * self.config.hps * self.multiplier * (86400 + self.config.addUsesPerDay * 60 * self.shop.calculator3)

    def buyable_hept(self, hept: Hepteract) -> int:
        return math.floor(self.wowAbyssals)

    @cached_property
    def orb_to_powder(self) -> float:
        denominator = math.prod(
            [
                1 / 100,
                1 + 1 / 50 * math.log2(self.challenge15Exponent / (7000000000000000 / 32)),
                1 + self.shop.powderEX / 50,
                1 + self.get_achievement(256) / 20,
                1 + self.get_achievement(257) / 20,
                1 + 0.01 * self.get_plat_upgrade(4, 1),
            ]
        )
        return 1/denominator

    @property
    def hepts_small_inc(self) -> float:
        return self.hepts.chronos.to_level * 0.0000001 / self.orb_to_powder / 250000
    
    @property
    def p44_noname(self) -> float:
        """ Dimnishing returns reduction value """
        return (1+0.0000001/2) ** ((1/6)+((1/750)*self.get_plat_upgrade(4, 4)))

    @property
    def powder_tomorrow(self) -> float:
        return self.overfluxPowder + self.overfluxOrbs / self.orb_to_powder

    @property
    def cube_from_powder(self) -> float:
        if self.powder_tomorrow > 10000:
            return 1+1/16* (math.log10(self.powder_tomorrow) ** 2) - 1 
        else:
            return 1+1/10000*self.powder_tomorrow - 1

    @property
    def powder_goal(self) -> float:
        """
        F5 = small incr in hept
        G7 = overflux powder
        E5 = p44_noname
        C3 = chronos increase
        E3 = hepts to level
        G5 = orb_to_powder

        =IF(Formulas!$F$5/((Formulas!G7)^(Formulas!E5-1)-1)<10000,
            IF(((Formulas!C3+1)^(1/Formulas!E3)-1)*10000*250000*Formulas!G5>1,
                Formulas!G7+ROUNDDOWN(Formulas!G3/24/250000)/Formulas!G5,10000),
            (Formulas!$F$5/((Formulas!$F$5/((Formulas!$F$5/((Formulas!$F$5/((Formulas!G7)^(Formulas!E5-1)-1))^(Formulas!E5-1)-1))^(Formulas!E5-1)-1))^(Formulas!E5-1)-1))/(B10+1)*B10)
        """
        if self.hepts_small_inc / ((self.overfluxPowder) ** (self.p44_noname - 1) - 1) < 10000:
            if self.chronos_increase + 1 ** (1 / self.hepts.chronos.to_level) - 1 * 1000 * 250000 * self.orb_to_powder > 1:
                return self.overfluxPowder + math.floor(self.hept_per_day / 24 / 250000) / self.orb_to_powder
            else:
                return 10000
        return (self.hepts_small_inc / ((self.hepts_small_inc / ((self.hepts_small_inc / ((self.hepts_small_inc / ((self.overfluxPowder) ** (self.p44_noname -1) -1)) ** (self.p44_noname -1) -1)) ** (self.p44_noname -1) -1)) ** (self.p44_noname -1) -1)) / (self.cube_from_powder + 1) * self.cube_from_powder

    @property
    def orbs_to_powder_goal(self) -> float:
        return (self.powder_goal - self.overfluxPowder) * self.orb_to_powder - self.overfluxOrbs
