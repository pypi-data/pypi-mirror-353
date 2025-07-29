"""
Meta data for code
"""

from .exam_test_case import ExamTestCase
from .exam_test_case_exam import ExamTestCaseExam
from .exam_test_result import ExamTestResult
from .exam_test_result_exam import ExamTestResultExam
from .helper_functions import check_for_tags as tags
from .helper_functions import find_path_to_assignment, import_module
from .run_tests import main as run

# Version structure major.minor[.patch][sub]
__version__ = "2.6.0"
