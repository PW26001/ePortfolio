"""
Unit 10 - Test-Driven Development and Behaviour Driven Development

A simplified course management module for an e-learning platform.

BDD describes the expected behaviour.

TDD then tests and develops the code needed to provide that behaviour
using Fail -> Pass -> Improve.
"""

from dataclasses import dataclass


@dataclass
class Course:
    course_id: int
    title: str
    tutor: str
    max_places: int


class InMemoryCourseRepository:
    def __init__(self):
        self.courses = {}

    def add_course(self, course):
        if course.course_id in self.courses:
            raise ValueError("Course ID already exists")

        self.courses[course.course_id] = course

    def get_course(self, course_id):
        return self.courses.get(course_id)

    def get_all_courses(self):
        return list(self.courses.values())

    def remove_course(self, course_id):
        if course_id not in self.courses:
            return False

        del self.courses[course_id]
        return True


class CourseService:
    def __init__(self, course_repository):
        self.course_repository = course_repository

    def add_course(self, course_id, title, tutor, max_places):
        if not title:
            raise ValueError("Course title is required")

        if not tutor:
            raise ValueError("Course tutor is required")

        if max_places <= 0:
            raise ValueError("Maximum places must be greater than zero")

        course = Course(
            course_id=course_id,
            title=title,
            tutor=tutor,
            max_places=max_places
        )

        self.course_repository.add_course(course)

        return course

    def get_course(self, course_id):
        return self.course_repository.get_course(course_id)

    def search_courses(self, search_term):
        search_term = search_term.lower()

        return [
            course
            for course in self.course_repository.get_all_courses()
            if search_term in course.title.lower()
        ]

    def remove_course(self, course_id):
        return self.course_repository.remove_course(course_id)


def main():
    course_repository = InMemoryCourseRepository()
    course_service = CourseService(course_repository)

    course_service.add_course(
        1,
        "Object-Oriented Programming",
        "Dr Smith",
        30
    )

    course_service.add_course(
        2,
        "Secure Software Design",
        "Dr Jones",
        25
    )

    results = course_service.search_courses("secure")

    for course in results:
        print(
            f"{course.course_id}: "
            f"{course.title} "
            f"with {course.tutor}"
        )


if __name__ == "__main__":
    main()