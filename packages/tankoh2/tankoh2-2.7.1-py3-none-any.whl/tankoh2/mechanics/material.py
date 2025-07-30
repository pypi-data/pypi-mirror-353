import json
import os
from collections import OrderedDict

from tankoh2 import log, programDir
from tankoh2.service.exception import Tankoh2Error

directions = OrderedDict(((11, 0), (22, 1), (12, 2)))  # dict referencing to index of stress array


class FrpMaterialProperties:
    def __init__(self, **kwargs):
        self.A_11 = None
        self.B_11 = None
        self.u_11 = None
        self.v_11 = None
        self.A_22 = None
        self.B_22 = None
        self.u_22 = None
        self.v_22 = None
        self.A_12 = None
        self.B_12 = None
        self.u_12 = None
        self.v_12 = None
        self.beta_1_11t = None
        self.beta_1_11c = None
        self.beta_1_22t = None
        self.beta_1_22c = None
        self.beta_1_12 = None
        self.beta_2_11t = None
        self.beta_2_11c = None
        self.beta_2_22t = None
        self.beta_2_22c = None
        self.beta_2_12 = None
        self.R_1_t = None
        self.R_1_c = None
        self.R_2_t = None
        self.R_2_c = None
        self.R_21 = None

        self._applyAttrs(**kwargs)

    def _applyAttrs(self, **kwargs):
        for key in kwargs:
            if not hasattr(self, key):
                log.debug(f'Unknown key "{key}" in class {self.__class__} with name "{str(self)} will be omitted"')
                continue
            setattr(self, key, kwargs[key])

    def readMaterial(self, materialFilename):
        """reads material properties from material filename. If materialFilename does not point to a file,
        it is assumed, that it references a file in tankoh2/data"""
        if not os.path.exists(materialFilename):
            materialFilename = os.path.join(programDir, "data", materialFilename)
        with open(materialFilename) as file:
            jsonDict = json.load(file)
        self._applyAttrs(**jsonDict["materials"]["1"]["umatProperties"]["data_sets"]["1"]["umatPuckProperties"])
        self._applyAttrs(**jsonDict["materials"]["1"]["umatProperties"]["data_sets"]["1"]["fatigueProperties"])
        return self

    def getStrengths(self, direction):
        if direction not in directions:
            raise Tankoh2Error(f"direction {direction} not in allDirections {directions}")
        if direction == 11:
            return self.R_1_t, self.R_1_c
        elif direction == 22:
            return self.R_2_t, self.R_2_c
        else:
            return self.R_21, self.R_21

    def getUV(self, direction):
        if direction not in directions:
            raise Tankoh2Error(f"direction {direction} not in allDirections {directions}")
        if direction == 11:
            return self.u_11, self.v_11
        elif direction == 22:
            return self.u_22, self.v_22
        else:
            return self.u_12, self.v_12

    def getCD(self, direction):
        if direction not in directions:
            raise Tankoh2Error(f"direction {direction} not in allDirections {directions}")
        if direction == 11:
            return self.A_11, self.B_11
        elif direction == 22:
            return self.A_22, self.B_22
        else:
            return self.A_12, self.B_12
