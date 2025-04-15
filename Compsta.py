"""
File: compsta.py
Author     : Arthur Morgado Teixeira
Email      : arthurmorgado7751@email.com
Github     : https://github.com/Morgadineo
Description: Compsta (ComplexityStatistic)
""" 

from typing import Generator
from C_module import *
from os import listdir
from tabulate import tabulate
import C_module

class ComplexityStatistic:
    """Docstring for ComplexityStatistic. """

    def __init__(self, dir_path: str):
        """
        :param dir_path: The relative or absolute directory name to be analyzed.
        """
        self.dir_name : str = dir_path  # Directory to be analyzed
        # ==> Files <== ===================================================== #
        self.files_qtt: int = self.count_pre_compiled_files()

        # ==> Metrics <== =================================================== #
        self.avg_total_lines    : float = 0.0
        self.avg_effective_lines: float = 0.0
        self.avg_n1             : float = 0.0
        self.avg_n2             : float = 0.0
        self.avg_N1             : float = 0.0
        self.avg_N2             : float = 0.0
        self.avg_vocabulary     : float = 0.0
        self.avg_lenght         : float = 0.0
        self.avg_estimated_len  : float = 0.0
        self.avg_volume         : float = 0.0
        self.avg_difficulty     : float = 0.0
        self.avg_level          : float = 0.0
        self.avg_intelligence   : float = 0.0
        self.avg_effort         : float = 0.0
        self.avg_time_required  : float = 0.0
        self.avg_delivered_bugs : float = 0.0

        self.avg_cognitive_complexity : float = 0.0
        self.avg_cyclomatic_complexity: float = 0.0

        self.calculate_metrics()



    def print_avg_metrics(self) -> None:
        """
        Print the average complexity metrics.
        """
        decimals: int = 2

        headers = ["Metric", "Average"]
        data = [["Total lines"          , round(self.avg_total_lines, decimals)],
                ["Effective lines"      , round(self.avg_effective_lines, decimals)],
                ["Distinct operators"   , round(self.avg_n1, decimals)],
                ["Distinct operands"    , round(self.avg_n2, decimals)],
                ["Total operators"      , round(self.avg_N1, decimals)],
                ["Total operands"       , round(self.avg_N2, decimals)],
                ["Vocabulary"           , round(self.avg_vocabulary, decimals)],
                ["Lenght"               , round(self.avg_lenght, decimals)],
                ["Estimated lenght"     , round(self.avg_estimated_len, decimals)],
                ["Volume"               , round(self.avg_volume, decimals)],
                ["Difficult"            , round(self.avg_difficulty, decimals)],
                ["Level"                , round(self.avg_level, decimals)],
                ["Intelligence"         , round(self.avg_intelligence, decimals)],
                ["Effort"               , round(self.avg_effort, decimals)],
                ["Time required"        , round(self.avg_time_required, decimals)],
                ["Delivered bugs"       , round(self.avg_delivered_bugs, decimals)],
                ["Cyclomatic complexity", round(self.avg_cyclomatic_complexity, decimals)],
                ["Cognitive complexity" , round(self.avg_cognitive_complexity, decimals)],
                ]
        print(tabulate(data, headers=headers, tablefmt="double_grid", numalign="right"))


    def calculate_metrics(self) -> None:
        """
        Calculate the average metrics.
        """
        avg_total_lines   : float = 0.0 
        avg_effect_lines  : float = 0.0
        avg_n1            : float = 0.0
        avg_n2            : float = 0.0
        avg_N1            : float = 0.0
        avg_N2            : float = 0.0
        avg_vocabulary    : float = 0.0
        avg_lenght        : float = 0.0
        avg_estimated_len : float = 0.0
        avg_volume        : float = 0.0
        avg_difficult     : float = 0.0
        avg_level         : float = 0.0
        avg_intelligence  : float = 0.0
        avg_effort        : float = 0.0
        avg_time_required : float = 0.0
        avg_delivered_bugs: float = 0.0

        avg_cognitive_complexity : float = 0.0
        avg_cyclomatic_complexity: float = 0.0

        for visitor in self.get_analyzed_files():
            """Sum the visitor complexity metrics"""
            avg_total_lines    += visitor.total_lines
            avg_effect_lines   += visitor.effective_lines
            avg_n1             += visitor.n1
            avg_n2             += visitor.n2
            avg_N1             += visitor.N1
            avg_N2             += visitor.N2
            avg_vocabulary     += visitor.vocabulary
            avg_lenght         += visitor.lenght
            avg_estimated_len  += visitor.estimated_len
            avg_volume         += visitor.volume
            avg_difficult      += visitor.difficulty
            avg_level          += visitor.level
            avg_intelligence   += visitor.intelligence
            avg_effort         += visitor.effort
            avg_time_required  += visitor.time_required
            avg_delivered_bugs += visitor.delivered_bugs

        self.avg_total_lines     = avg_total_lines / self.files_qtt
        self.avg_effective_lines = avg_effect_lines / self.files_qtt
        self.avg_n1              = avg_n1 / self.files_qtt
        self.avg_n2              = avg_n2 / self.files_qtt
        self.avg_N1              = avg_N1 / self.files_qtt
        self.avg_N2              = avg_N2 / self.files_qtt
        self.avg_vocabulary      = avg_vocabulary / self.files_qtt
        self.avg_lenght          = avg_lenght / self.files_qtt
        self.avg_estimated_len   = avg_estimated_len / self.files_qtt
        self.avg_volume          = avg_volume / self.files_qtt
        self.avg_difficulty      = avg_difficult / self.files_qtt
        self.avg_level           = avg_level / self.files_qtt
        self.avg_intelligence    = avg_intelligence / self.files_qtt
        self.avg_effort          = avg_effort / self.files_qtt
        self.avg_time_required   = avg_time_required / self.files_qtt
        self.avg_delivered_bugs  = avg_delivered_bugs / self.files_qtt

        self.avg_cognitive_complexity  = avg_cognitive_complexity / self.files_qtt
        self.avg_cyclomatic_complexity = avg_cyclomatic_complexity / self.files_qtt


    def get_analyzed_files(self) -> Generator[ComplexityVisitor, None, None]:
        """
        Get all the analized files, create a ComplexityVisitor and return then.

        :param dir_path: Directory path to analyze.

        :return:
            A ComplexityVisitor object that store the source code complexity metrics.
        """
        for precompiled_file in self.get_precompiled_files():
            precompiled_file = precompiled_file[:-2] # Remove the file extension.
            analized_file: ComplexityVisitor = C_module.ComplexityVisitor(precompiled_file)
            yield analized_file

    def get_precompiled_files(self) -> Generator[str, None, None]:
        """
        Get all the precompiled files present in "dir_path" and return it one in one.
        """
        for filename in listdir(self.dir_name):
            if filename[-2:] == ".i":
                yield filename

    def count_pre_compiled_files(self) -> int:
        """
        Count the amount of pre-compiled (extension '.i') files present in a directory.

        :return: Quantity of .i files.
        """
        files_qtt: int = 0
        for _ in self.get_precompiled_files():
            files_qtt += 1

        return files_qtt
    
if __name__ == "__main__":
    compsta = ComplexityStatistic("Examples") 
    compsta.print_avg_metrics()
