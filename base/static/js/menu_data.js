// Menu data - single source of truth
const menuData = {
    about: {
        title: 'About',
        sections: [
            {
                title: 'Our College',
                links: [
                    { text: "Dean's Welcome", href: '/about/deans-welcome/' },
                    { text: 'Vision, Mission & Strategic Plan', href: '/about/mission-vision-strategic-plan/' },
                    { text: 'Administration', href: '/about/administration-index/' },
                    { text: 'People', href: '/people/' }
                ]
            },
            {
                title: 'Governance',
                links: [
                    { text: 'College By-Laws', href: '/about/college-by-laws/' },
                    { text: 'Board of Advisors', href: '/about/board-of-advisors/' },
                    { text: 'Standing Committees', href: '/about/standing-committees/' }
                ]
            },
            {
                title: 'Community',
                links: [
                    { text: 'News & Announcements', href: '/news/' },
                    { text: 'Work with us', href: '/about/work-with-us/' },
                    { text: 'Reports & Newsletters', href: '/about/reports/' },
                    { text: 'Give to us!', href: '/about/give-to-us/' }
                ]
            }
        ]
    },
    students: {
        title: 'Students',
        sections: [
            {
                title: 'Admission',
                links: [
                    { text: 'Undergraduate', href: 'https://tsu.edu/admissions/freshman.php'},
                    { text: 'Graduate', href: 'https://tsu.edu/academics/colleges-and-schools/graduate-school/apply-now.php'},
                    { text: 'International', href: 'https://tsu.edu/admissions/international/index.php' }
                ]
            },
            {
                title: 'Office of Student Services and Instructional Support',
                links: [
                    { text: 'Student Services', href: '/students/services/' },
                    { text: 'Advisors & Support', href: '/students/advisors/' },
                    { text: 'Links for Students', href: '/students/links' }
                ]
            },
            {
                title: 'Student Life',
                links: [
                    { text: 'Summer Programs & Internships', href: '/internships/' },
                    { text: 'Scholarships & Fellowships', href: '/scholarships/' },
                    { text: 'Student Organizations', href: '/students/organizations' }
                ]
            }
        ]
    },
    academics: {
        title: 'Academics',
        sections: [
            {
                title: 'Programs',
                links: [
                    { text: 'Undergraduate', href: '/programs/undergraduate-index/' },
                    { text: 'Graduate', href: '/programs/undergraduate-index/' },
                    { text: 'Accredited Programs', href: '/programs/accreditation/' }
                ]
            },
            {
                title: 'Departments',
                links: [
                    { text: 'Biology', href: '/biology/' },
                    { text: 'Chemistry', href: '/chemistry/' },
                    { text: 'Mathematical Sciences', href: '/mathematics/' },
                    { text: 'Physics', href: '/physics/' }
                ]
            },
            {
                title: '...',
                links: [
                    { text: 'Aerospace & Mechanical Engineering', href: '/asme/' },
                    { text: 'Chemical Engineering & Environmental Toxicology', href: '/ceet/' },
                    { text: 'Civil Engineering & Transportation Studies', href: '/cets/' },
                    { text: 'Electrical Engineering & Computer Science', href: '/eecs/' },
                ]
            }
        ]
    },
    research: {
        title: 'Research',
        sections: [
            {
                title: 'Overview',
                links: [
                    { text: 'Highlights & Strategic Areas', href: '/research/highlights-strategic-areas' },
                    { text: 'Research Committee', href: '/research/committee/' },
                    { text: 'Seminars & Events', href: '/research/seminars/' },
                    { text: 'Student Research Opportunities', href: '/research/student-opportunities/' },
                    { text: 'Core Research Resources', href: '/research/core-resources/' }
                ]
            },
            {
                title: 'Centers',
                links: [
                    { text: 'High Performance Computing', href: '/research/hppc/' },
                    { text: 'Transportation, Training, and Research', href: '/research/ttr/' },
                    { text: 'Innovative Transportation Research', href: '/research/irt' },
                    { text: 'Scientific Machine Learning for Material Science', href: '/research/sciml-ms' }
                ]
            },
            {
                title: 'Research Programs',
                links: [
                    { text: 'Microplastics Impact', href: '/research/microplastics/' },
                    { text: 'Geostatistical Intelligence', href: '/research/geostats/' },
                    { text: 'Digital Twins and Robotics', href: '/research/digital-twins/' }
                ]
            }
        ]
    }
};