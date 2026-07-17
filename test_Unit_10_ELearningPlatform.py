"""
Unit tests for Unit10_ELearningPlatform.py

The tests describe the expected behaviour before relying on the
implementation.

BDD style:
Given a course does not already exist,
when an administrator adds the course,
then it appears in the course catalogue.
"""

import unittest

from Unit10_ELearningPlatform import (
    CourseService,
    InMemoryCourseRepository
)


class CourseServiceTests(unittest.TestCase):

    def setUp(self):
        self.course_repository = InMemoryCourseRepository()
        self.course_service = CourseService(
            self.course_repository
        )

    def test_add_course_valid_course_course_is_added(self):
        course = self.course_service.add_course(
            1,
            "Object-Oriented Programming",
            "Dr Smith",
            30
        )

        saved_course = self.course_service.get_course(1)

        self.assertEqual(course, saved_course)
        self.assertEqual("Object-Oriented Programming", saved_course.title)

    def test_add_course_empty_title_value_error(self):
        with self.assertRaises(ValueError):
            self.course_service.add_course(
                1,
                "",
                "Dr Smith",
                30
            )

    def test_add_course_empty_tutor_value_error(self):
        with self.assertRaises(ValueError):
            self.course_service.add_course(
                1,
                "Object-Oriented Programming",
                "",
                30
            )

    def test_add_course_zero_places_value_error(self):
        with self.assertRaises(ValueError):
            self.course_service.add_course(
                1,
                "Object-Oriented Programming",
                "Dr Smith",
                0
            )

    def test_add_course_duplicate_course_id_value_error(self):
        self.course_service.add_course(
            1,
            "Object-Oriented Programming",
            "Dr Smith",
            30
        )

        with self.assertRaises(ValueError):
            self.course_service.add_course(
                1,
                "Secure Software Design",
                "Dr Jones",
                25
            )

    def test_get_course_existing_course_course_returned(self):
        self.course_service.add_course(
            1,
            "Object-Oriented Programming",
            "Dr Smith",
            30
        )

        course = self.course_service.get_course(1)

        self.assertEqual("Object-Oriented Programming", course.title)

    def test_get_course_missing_course_none_returned(self):
        course = self.course_service.get_course(999)

        self.assertIsNone(course)

    def test_search_courses_matching_title_courses_returned(self):
        self.course_service.add_course(
            1,
            "Object-Oriented Programming",
            "Dr Smith",
            30
        )

        self.course_service.add_course(
            2,
            "Secure Software Design",
            "Dr Jones",
            25
        )

        results = self.course_service.search_courses("secure")

        self.assertEqual(1, len(results))
        self.assertEqual("Secure Software Design", results[0].title)

    def test_remove_course_existing_course_true_returned(self):
        self.course_service.add_course(
            1,
            "Object-Oriented Programming",
            "Dr Smith",
            30
        )

        result = self.course_service.remove_course(1)

        self.assertTrue(result)
        self.assertIsNone(self.course_service.get_course(1))

    def test_remove_course_missing_course_false_returned(self):
        result = self.course_service.remove_course(999)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
