from unittest import TestCase

from pyecsca.ec.curve import EllipticCurve
from pyecsca.ec.mod import Mod
from pyecsca.ec.model import ShortWeierstrassModel, MontgomeryModel
from pyecsca.ec.mult import (LTRMultiplier, RTLMultiplier, LadderMultiplier, BinaryNAFMultiplier,
                             WindowNAFMultiplier, SimpleLadderMultiplier, CoronMultiplier)
from pyecsca.ec.point import Point


class ScalarMultiplierTests(TestCase):

    def setUp(self):
        self.p = 0xfffffffdffffffffffffffffffffffff
        self.coords = ShortWeierstrassModel().coordinates["projective"]
        self.base = Point(self.coords, X=Mod(0x161ff7528b899b2d0c28607ca52c5b86, self.p),
                          Y=Mod(0xcf5ac8395bafeb13c02da292dded7a83, self.p),
                          Z=Mod(1, self.p))
        self.secp128r1 = EllipticCurve(ShortWeierstrassModel(), self.coords,
                                       dict(a=0xfffffffdfffffffffffffffffffffffc,
                                            b=0xe87579c11079f43dd824993c2cee5ed3),
                                       Point(self.coords, X=Mod(0, self.p), Y=Mod(1, self.p),
                                             Z=Mod(0, self.p)))

        self.coords25519 = MontgomeryModel().coordinates["xz"]
        self.p25519 = 0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffed
        self.base25519 = Point(self.coords25519, X=Mod(9, self.p25519),
                               Z=Mod(1, self.p25519))
        self.curve25519 = EllipticCurve(MontgomeryModel(), self.coords25519,
                                        dict(a=486662, b=1),
                                        Point(self.coords25519,
                                              X=Mod(0, self.p25519), Z=Mod(1, self.p25519)))

    def test_rtl(self):
        mult = RTLMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                             self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"])
        res = mult.multiply(10, self.base)
        other = mult.multiply(5, self.base)
        other = mult.multiply(2, other)
        self.assertEqual(res, other)

    def test_ltr(self):
        mult = LTRMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                             self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"])
        res = mult.multiply(10, self.base)
        other = mult.multiply(5, self.base)
        other = mult.multiply(2, other)
        self.assertEqual(res, other)

    def test_coron(self):
        mult = CoronMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                               self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"])
        res = mult.multiply(10, self.base)
        other = mult.multiply(5, self.base)
        other = mult.multiply(2, other)
        self.assertEqual(res, other)

    def test_ladder(self):
        mult = LadderMultiplier(self.curve25519, self.coords25519.formulas["ladd-1987-m"],
                                self.coords25519.formulas["dbl-1987-m"],
                                self.coords25519.formulas["scale"])
        res = mult.multiply(15, self.base25519)
        other = mult.multiply(5, self.base25519)
        other = mult.multiply(3, other)
        self.assertEqual(res, other)

    def test_simple_ladder(self):
        mult = SimpleLadderMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                      self.coords.formulas["dbl-1998-cmo"],
                                      self.coords.formulas["z"])
        res = mult.multiply(10, self.base)
        other = mult.multiply(5, self.base)
        other = mult.multiply(2, other)
        self.assertEqual(res, other)

    def test_ladder_differential(self):
        ladder = LadderMultiplier(self.curve25519, self.coords25519.formulas["ladd-1987-m"],
                                  self.coords25519.formulas["dbl-1987-m"],
                                  self.coords25519.formulas["scale"])
        # TODO: fix this
        differential = SimpleLadderMultiplier(self.curve25519,
                                              self.coords25519.formulas["dadd-1987-m"],
                                              self.coords25519.formulas["dbl-1987-m"],
                                              self.coords25519.formulas["scale"])
        res_ladder = ladder.multiply(15, self.base25519)
        res_differential = differential.multiply(15, self.base25519)
        self.assertEqual(res_ladder, res_differential)

    def test_binary_naf(self):
        mult = BinaryNAFMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"],
                                   self.coords.formulas["neg"], self.coords.formulas["z"])
        res = mult.multiply(10, self.base)
        other = mult.multiply(5, self.base)
        other = mult.multiply(2, other)
        self.assertEqual(res, other)

    def test_window_naf(self):
        mult = WindowNAFMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"],
                                   self.coords.formulas["neg"], 3, self.coords.formulas["z"])
        res = mult.multiply(10, self.base)
        other = mult.multiply(5, self.base)
        other = mult.multiply(2, other)
        self.assertEqual(res, other)

        mult = WindowNAFMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"],
                                   self.coords.formulas["neg"], 3, self.coords.formulas["z"],
                                   precompute_negation=True)
        res_precompute = mult.multiply(10, self.base)
        self.assertEqual(res_precompute, res)

    def test_basic_multipliers(self):
        ltr = LTRMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                            self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"])
        res_ltr = ltr.multiply(10, self.base)
        rtl = RTLMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                            self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"])
        res_rtl = rtl.multiply(10, self.base)
        self.assertEqual(res_ltr, res_rtl)

        ltr_always = LTRMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"],
                                   always=True)
        rtl_always = RTLMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"], self.coords.formulas["z"],
                                   always=True)
        res_ltr_always = ltr_always.multiply(10, self.base)
        res_rtl_always = rtl_always.multiply(10, self.base)
        self.assertEqual(res_ltr, res_ltr_always)
        self.assertEqual(res_rtl, res_rtl_always)

        bnaf = BinaryNAFMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"],
                                   self.coords.formulas["neg"], self.coords.formulas["z"])
        res_bnaf = bnaf.multiply(10, self.base)
        self.assertEqual(res_bnaf, res_ltr)

        wnaf = WindowNAFMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                   self.coords.formulas["dbl-1998-cmo"],
                                   self.coords.formulas["neg"], 3, self.coords.formulas["z"])
        res_wnaf = wnaf.multiply(10, self.base)
        self.assertEqual(res_wnaf, res_ltr)

        ladder = SimpleLadderMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                        self.coords.formulas["dbl-1998-cmo"],
                                        self.coords.formulas["z"])
        res_ladder = ladder.multiply(10, self.base)
        self.assertEqual(res_ladder, res_ltr)

        coron = CoronMultiplier(self.secp128r1, self.coords.formulas["add-1998-cmo"],
                                self.coords.formulas["dbl-1998-cmo"],
                                self.coords.formulas["z"])
        res_coron = coron.multiply(10, self.base)
        self.assertEqual(res_coron, res_ltr)