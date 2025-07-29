# This file is part of Monitizer, a tool for optimizing and evaluating neural network monitors:
# https://gitlab.com/live-lab/software/monitizer/
#
# SPDX-FileCopyrightText: 2023 Stefanie Mohr
#
# SPDX-License-Identifier: Apache-2.0

def get_all_monitors() -> list:
    return ["box", "dice", "energy", "entropy", "gauss", "gradnorm", "klmatching", "knn", "maxlogit", "mds",
            "msp", "odin", "react", "rmd", "she", "temperature", "vim", "ash_p", "ash_b", "ash_rand", "ash_s",
            "gauss-one", "mds_new", "rmd_new"]


def get_all_auroc_monitors() -> list:
    return ["dice", "energy", "entropy", "gradnorm", "klmatching", "knn", "maxlogit", #"mds", "mds_new",
            "msp", "odin", "react", #"rmd",
            "she", "temperature", "vim", "ash_p", "ash_b", "ash_rand", "ash_s",
            "gauss-one", "rmd_new"]


def get_all_monitor_names() -> list:
    return ["ash", "box", "dice", "energy", "entropy", "gauss", "gradnorm", "klmatching", "knn", "maxlogit", "mds",
            "msp", "odin", "react", "rmd", "she", "temperature", "vim", "ash_p", "ash_b", "ash_rand", "ash_s",
            "gauss-one", "mds_new", "rmd_new"]


def get_monitors_and_parameters() -> dict:
    return {
        "ash": 3,
        "box": 2,
        "dice": 2,
        "energy": 2,
        "entropy": 1,
        "gauss": 2,
        "gradnorm": 2,
        "klmatching": 1,
        "knn": 1,
        "maxlogit": 1,
        "mds": 4,
        "msp": 1,
        "odin": 3,
        "react": 3,
        "rmd": 2,
        "she": 1,
        "temperature": 1,
        "vim": 2,
        "gauss-one": 1,
    }
