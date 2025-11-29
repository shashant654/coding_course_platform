# courses/management/commands/seed_courses.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Section, Lecture
from decimal import Decimal
import random
from io import BytesIO
from PIL import Image

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample course data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--courses',
            type=int,
            default=12,
            help='Number of courses to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        num_courses = options['courses']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Lecture.objects.all().delete()
            Section.objects.all().delete()
            Course.objects.all().delete()
            Category.objects.all().delete()
            # Keep users intact
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        self.stdout.write(self.style.SUCCESS('Creating categories...'))
        categories = self.create_categories()

        self.stdout.write(self.style.SUCCESS('Creating instructors...'))
        instructors = self.create_instructors()

        self.stdout.write(self.style.SUCCESS(f'Creating {num_courses} courses...'))
        courses = self.create_courses(num_courses, categories, instructors)

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(courses)} courses!'))

    def create_categories(self):
        """Create course categories"""
        categories_data = [
            {
                'name': 'Web Development',
                'description': 'Learn to build modern web applications',
                'icon': 'fas fa-code'
            },
            {
                'name': 'Python Programming',
                'description': 'Master Python from basics to advanced',
                'icon': 'fab fa-python'
            },
            {
                'name': 'Data Science',
                'description': 'Analyze data and build ML models',
                'icon': 'fas fa-chart-line'
            },
            {
                'name': 'Mobile Development',
                'description': 'Build iOS and Android apps',
                'icon': 'fas fa-mobile-alt'
            },
            {
                'name': 'DevOps',
                'description': 'Learn deployment and automation',
                'icon': 'fas fa-server'
            },
            {
                'name': 'Database',
                'description': 'Master SQL and NoSQL databases',
                'icon': 'fas fa-database'
            }
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  ✓ Created category: {category.name}')

        return categories

    def create_instructors(self):
        """Create instructor users"""
        instructors_data = [
            {'username': 'john_smith', 'first_name': 'John', 'last_name': 'Smith', 'email': 'john@example.com'},
            {'username': 'sarah_jones', 'first_name': 'Sarah', 'last_name': 'Jones', 'email': 'sarah@example.com'},
            {'username': 'mike_wilson', 'first_name': 'Mike', 'last_name': 'Wilson', 'email': 'mike@example.com'},
            {'username': 'emma_brown', 'first_name': 'Emma', 'last_name': 'Brown', 'email': 'emma@example.com'},
            {'username': 'david_lee', 'first_name': 'David', 'last_name': 'Lee', 'email': 'david@example.com'},
        ]

        instructors = []
        for data in instructors_data:
            instructor, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_instructor': True,
                    'is_active': True
                }
            )
            if created:
                instructor.set_password('password123')
                instructor.save()
                self.stdout.write(f'  ✓ Created instructor: {instructor.get_full_name()}')
            instructors.append(instructor)

        return instructors

    def generate_thumbnail(self):
        """Generate a simple colored thumbnail image"""
        # Create a simple colored image
        colors = [
            (74, 144, 226),   # Blue
            (52, 168, 83),    # Green
            (234, 67, 53),    # Red
            (251, 188, 5),    # Yellow
            (156, 39, 176),   # Purple
            (255, 112, 67),   # Orange
        ]
        
        color = random.choice(colors)
        img = Image.new('RGB', (800, 450), color)
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        return ContentFile(buffer.read(), name='thumbnail.jpg')

    def create_courses(self, num_courses, categories, instructors):
        """Create courses with sections and lectures"""
        # Category mapping for exact matches
        category_map = {
            'Web Development': 'Web Development',
            'Python': 'Python Programming',
            'Data Science': 'Data Science',
            'Mobile': 'Mobile Development',
            'DevOps': 'DevOps',
            'Database': 'Database'
        }
        
        courses_data = [
            {
                'title': 'Complete Python Bootcamp: From Zero to Hero',
                'category': 'Python Programming',
                'level': 'beginner',
                'short_description': 'Learn Python from scratch with hands-on projects and real-world examples',
                'price': 89.99,
                'discount_price': 49.99,
            },
            {
                'title': 'Web Development Masterclass: HTML, CSS, JavaScript',
                'category': 'Web Development',
                'level': 'beginner',
                'short_description': 'Build responsive websites from scratch using modern web technologies',
                'price': 79.99,
                'discount_price': 39.99,
            },
            {
                'title': 'React - The Complete Guide 2024',
                'category': 'Web Development',
                'level': 'intermediate',
                'short_description': 'Master React JS including Hooks, Context API, Redux, and Next.js',
                'price': 99.99,
                'discount_price': 59.99,
            },
            {
                'title': 'Data Science and Machine Learning with Python',
                'category': 'Data Science',
                'level': 'intermediate',
                'short_description': 'Learn data analysis, visualization, and machine learning algorithms',
                'price': 109.99,
                'discount_price': 69.99,
            },
            {
                'title': 'Django for Beginners: Build Web Apps with Python',
                'category': 'Web Development',
                'level': 'beginner',
                'short_description': 'Create powerful web applications using Django framework',
                'price': 0,
                'discount_price': None,
            },
            {
                'title': 'Advanced SQL for Data Analysis',
                'category': 'Database',
                'level': 'advanced',
                'short_description': 'Master complex queries, optimization, and database design',
                'price': 79.99,
                'discount_price': 44.99,
            },
            {
                'title': 'Docker and Kubernetes: The Complete Guide',
                'category': 'DevOps',
                'level': 'intermediate',
                'short_description': 'Learn containerization and orchestration from scratch',
                'price': 94.99,
                'discount_price': 54.99,
            },
            {
                'title': 'iOS App Development with Swift',
                'category': 'Mobile Development',
                'level': 'intermediate',
                'short_description': 'Build native iOS applications using Swift and SwiftUI',
                'price': 99.99,
                'discount_price': None,
            },
            {
                'title': 'Introduction to Artificial Intelligence',
                'category': 'Data Science',
                'level': 'beginner',
                'short_description': 'Understand AI concepts, neural networks, and deep learning basics',
                'price': 0,
                'discount_price': None,
            },
            {
                'title': 'Full Stack Web Development Bootcamp',
                'category': 'Web Development',
                'level': 'intermediate',
                'short_description': 'Become a full stack developer with MERN stack',
                'price': 119.99,
                'discount_price': 79.99,
            },
            {
                'title': 'PostgreSQL for Developers',
                'category': 'Database',
                'level': 'intermediate',
                'short_description': 'Master PostgreSQL database management and optimization',
                'price': 69.99,
                'discount_price': 34.99,
            },
            {
                'title': 'Flutter & Dart - Complete App Development',
                'category': 'Mobile Development',
                'level': 'beginner',
                'short_description': 'Build cross-platform mobile apps with Flutter',
                'price': 89.99,
                'discount_price': 49.99,
            },
        ]

        # Use only the courses we need
        courses_to_create = courses_data[:min(num_courses, len(courses_data))]
        
        # If more courses needed, repeat with variations
        while len(courses_to_create) < num_courses:
            base_course = random.choice(courses_data)
            variation = base_course.copy()
            variation['title'] = f"{base_course['title']} - Advanced Edition"
            courses_to_create.append(variation)

        courses = []
        for i, course_data in enumerate(courses_to_create):
            # Use exact category name match to avoid duplicates
            try:
                category = Category.objects.get(name=course_data['category'])
            except Category.DoesNotExist:
                # Fallback to first matching category
                category = categories[0]
            instructor = random.choice(instructors)
            
            # Detailed description
            detailed_desc = f"""
This comprehensive course on {course_data['title']} will take you from beginner to advanced level.

You'll learn:
- Core concepts and fundamentals
- Best practices and industry standards
- Real-world project development
- Advanced techniques and patterns

Whether you're just starting out or looking to enhance your skills, this course has everything you need to succeed.

Our hands-on approach ensures you learn by doing, with plenty of exercises, projects, and quizzes to test your knowledge.

By the end of this course, you'll have the confidence and skills to build professional-grade applications.
"""

            requirements = """
- Basic computer skills
- Access to a computer with internet connection
- Willingness to learn and practice
- No prior programming experience required (for beginner courses)
"""

            what_you_will_learn = """
- Master the core concepts
- Build real-world projects
- Write clean, efficient code
- Understand best practices
- Deploy applications
- Debug and troubleshoot
"""

            course = Course.objects.create(
                title=course_data['title'],
                slug=slugify(course_data['title'] + str(i)),
                instructor=instructor,
                category=category,
                short_description=course_data['short_description'],
                detailed_description=detailed_desc.strip(),
                price=Decimal(str(course_data['price'])),
                discount_price=Decimal(str(course_data['discount_price'])) if course_data['discount_price'] else None,
                level=course_data['level'],
                language='English',
                duration_hours=random.randint(8, 40),
                total_lectures=random.randint(50, 200),
                requirements=requirements.strip(),
                what_you_will_learn=what_you_will_learn.strip(),
                is_published=True,
                is_featured=random.choice([True, False]),
                average_rating=Decimal(str(round(random.uniform(4.0, 5.0), 1))),
                total_enrollments=random.randint(100, 5000)
            )

            # Add thumbnail
            course.thumbnail_image = self.generate_thumbnail()
            course.save()

            # Create sections
            num_sections = random.randint(4, 8)
            for j in range(num_sections):
                section = Section.objects.create(
                    course=course,
                    title=f"Section {j+1}: {self.get_section_title(course_data['category'])}",
                    description=f"In this section, you'll learn important concepts and techniques.",
                    order=j
                )

                # Create lectures
                num_lectures = random.randint(5, 12)
                for k in range(num_lectures):
                    Lecture.objects.create(
                        section=section,
                        title=f"Lecture {k+1}: {self.get_lecture_title()}",
                        description="Detailed explanation of the topic with examples.",
                        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        duration_minutes=random.randint(5, 25),
                        order=k,
                        is_preview=(k == 0)  # First lecture is preview
                    )

            courses.append(course)
            self.stdout.write(f'  ✓ Created course: {course.title}')

        return courses

    def get_section_title(self, category):
        """Generate section titles based on category"""
        titles = {
            'Web Development': ['Getting Started', 'HTML Basics', 'CSS Styling', 'JavaScript Fundamentals', 'Advanced Topics', 'Project Building'],
            'Python Programming': ['Python Basics', 'Data Types', 'Functions', 'OOP Concepts', 'File Handling', 'Advanced Python'],
            'Data Science': ['Introduction to Data Science', 'Data Analysis', 'Visualization', 'Machine Learning', 'Deep Learning', 'Projects'],
            'Mobile Development': ['Setup', 'UI Basics', 'Navigation', 'State Management', 'API Integration', 'Publishing'],
            'DevOps': ['Introduction', 'Containers', 'Orchestration', 'CI/CD', 'Monitoring', 'Best Practices'],
            'Database': ['SQL Basics', 'Queries', 'Joins', 'Optimization', 'Advanced Topics', 'Real Projects']
        }
        
        category_key = next((k for k in titles.keys() if k in category), 'Web Development')
        return random.choice(titles[category_key])

    def get_lecture_title(self):
        """Generate random lecture titles"""
        topics = [
            'Introduction and Overview',
            'Core Concepts Explained',
            'Hands-on Practice',
            'Common Patterns',
            'Best Practices',
            'Real-world Example',
            'Advanced Techniques',
            'Troubleshooting Tips',
            'Project Setup',
            'Building Features',
            'Testing and Debugging',
            'Optimization Strategies'
        ]
        return random.choice(topics)