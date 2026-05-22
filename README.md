Photo Album Management System



A full-featured Django web application for organizing and sharing photos in albums.

Images are stored on Cloudinary, the database runs on PostgreSQL in production,

and the app is deployment-ready for Render.





Overview



Users can create albums, upload photos into them, and control who can see or edit

their content. Staff accounts have unrestricted access across all albums.





Features



\- User registration and login with Django's built-in auth system

\- Create, edit, and delete albums

\- Upload, edit, and delete photos per album

\- Public, private, and collaborator-based album visibility

\- Role-based access control (RBAC) enforced at the view level

\- Search albums and photos by name or description

\- Paginated album list and photo grid (12 per page)

\- Flash messages for all user actions

\- Production security headers (HSTS, SSL redirect, XSS protection, etc.)

\- Images served via Cloudinary; static files via WhiteNoise





Tech Stack



\- Python / Django 6.0

\- PostgreSQL (psycopg2-binary) in production, SQLite locally

\- Cloudinary for image upload and storage

\- django-cloudinary-storage

\- WhiteNoise for static file serving

\- Gunicorn as the production WSGI server

\- dj-database-url for database config

\- python-dotenv for environment variable loading

\- Pillow





Project Structure



photo-album/

&#x20;   gallery/

&#x20;       migrations/         Database migrations

&#x20;       templates/

&#x20;           gallery/

&#x20;               album/      Album list, detail, form, confirm delete templates

&#x20;               auth/       Login and register templates

&#x20;               photo/      Photo form and confirm delete templates

&#x20;           base.html       Base layout template

&#x20;       admin.py

&#x20;       apps.py

&#x20;       forms.py            AlbumForm and PhotoForm

&#x20;       mixins.py           RBAC permission mixins

&#x20;       models.py           Album and Photo models

&#x20;       urls.py             URL routes

&#x20;       views.py            Class-based views

&#x20;   recipe\_project/

&#x20;       settings.py

&#x20;       urls.py

&#x20;       wsgi.py

&#x20;       asgi.py

&#x20;   manage.py

&#x20;   requirements.txt

&#x20;   build.sh





Models



Album

&#x20;   - name (CharField)

&#x20;   - description (TextField, optional)

&#x20;   - owner (ForeignKey to User)

&#x20;   - collaborators (ManyToManyField to User, optional)

&#x20;   - is\_public (BooleanField)

&#x20;   - created\_at, updated\_at (auto timestamps)



Photo

&#x20;   - album (ForeignKey to Album)

&#x20;   - title (CharField)

&#x20;   - description (TextField, optional)

&#x20;   - image (CloudinaryField)

&#x20;   - uploaded\_by (ForeignKey to User)

&#x20;   - uploaded\_at, updated\_at (auto timestamps)





URL Routes



&#x20;   /register/                          Register a new account

&#x20;   /login/                             Login

&#x20;   /logout/                            Logout

&#x20;   /                                   Album list

&#x20;   /albums/new/                        Create album

&#x20;   /albums/<pk>/                       Album detail

&#x20;   /albums/<pk>/edit/                  Edit album

&#x20;   /albums/<pk>/delete/                Delete album

&#x20;   /albums/<album\_pk>/photos/upload/   Upload photo

&#x20;   /photos/<pk>/edit/                  Edit photo

&#x20;   /photos/<pk>/delete/                Delete photo





Permissions



Role                  Can Do

\--------------------  -------------------------------------------------------

Unauthenticated       Redirected to login for all pages

Authenticated user    Create albums; view own, public, and shared albums

Album owner / staff   Full CRUD on that album and all its photos

Non-owner             Read-only; raises 403 on any edit or delete attempt





Environment Variables



SECRET\_KEY                  Django secret key

DEBUG                       Set to True for local development only

DATABASE\_URL                PostgreSQL connection string

CLOUDINARY\_CLOUD\_NAME       Cloudinary cloud name

CLOUDINARY\_API\_KEY          Cloudinary API key

CLOUDINARY\_API\_SECRET       Cloudinary API secret

ALLOWED\_HOSTS               Comma-separated hostnames (optional)





Local Setup (Windows PowerShell)



1\. Clone the repository



&#x20;   git clone <your-repo-url>

&#x20;   cd photo-album



2\. Create and activate a virtual environment



&#x20;   python -m venv .venv

&#x20;   .venv\\Scripts\\Activate.ps1



&#x20;   If you get a script execution error, run this first:

&#x20;   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser



3\. Install dependencies



&#x20;   pip install -r requirements.txt



4\. Create a .env file in the project root



&#x20;   SECRET\_KEY=your\_secret\_key

&#x20;   DEBUG=True

&#x20;   DATABASE\_URL=postgres://user:password@localhost:5432/photo\_album

&#x20;   CLOUDINARY\_CLOUD\_NAME=your\_cloud\_name

&#x20;   CLOUDINARY\_API\_KEY=your\_api\_key

&#x20;   CLOUDINARY\_API\_SECRET=your\_api\_secret



5\. Run migrations



&#x20;   python manage.py migrate



6\. Create a superuser



&#x20;   python manage.py createsuperuser



7\. Run the development server



&#x20;   python manage.py runserver



&#x20;   Open http://127.0.0.1:8000 in your browser.





Deployment (Render)



1\. Push your code to GitHub.

2\. Create a new Web Service on Render and connect your repository.

3\. Set the build command:



&#x20;   ./build.sh



4\. Set the start command:



&#x20;   gunicorn recipe\_project.wsgi



5\. Add all environment variables from the list above in the Render dashboard.

6\. Set DEBUG=False in production.



Render automatically provides the RENDER\_EXTERNAL\_HOSTNAME which is added

to ALLOWED\_HOSTS by the settings module.





Security Notes



In production (DEBUG=False), the following are automatically enabled:

\- HTTPS redirect

\- Secure session and CSRF cookies

\- HSTS with subdomains and preload (1 year)

\- XSS filter and content type sniffing protection

\- X-Frame-Options set to DENY

