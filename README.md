# Team *kinkajou* Small Group project

## Team members
The members of the team are:
- *Sihas Abeywickrama*
- *Raphael Ahiable*
- *Vraj Parmar*
- *Shankhi Sinha*
- *Ahmet Taramis*

## Project structure
The project is called `task_manager`.  It currently consists of a single app `tasks`.

## Deployed version of the application
The deployed version of the application can be found at [link_to_project](https://vrajparmar2003.pythonanywhere.com).  

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`

## AI/Website Usage Declaration
**Vraj Parmar:**
- I used ChatGPT to guide the development of the update_request_status function in tutorials/views.py. It helped me map out the logical steps required to allocate or unallocate lesson requests, which subsequently create or cancel AllocatedLessons.

- To ensure comprehensive test coverage, I consulted ChatGPT for identifying any missing scenarios in the following test files:
  - test_allocated_lesson_model.py
  - test_user_model.py
  - test_admin_view_requests.py
  - test_cancel_lesson.py
  - test_create_lesson_request.py
  - test_get_term_date_range.py
  - test_sign_up_view.py

- ChatGPT was instrumental in resolving logical issues in the following test cases:
  - test_student_view_requests.py
  - test_update_request_status.py
  - test_asgi.py
  - test_urls.py
  - test_wsgi.py

- I refactored the is_admin, is_tutor, and is_student functions, originally written as simple functions in tutorials/views.py, into proper decorators placed in helper.py. ChatGPT assisted in this restructuring to align with best practices.
- Leveraging ChatGPT significantly enhanced my understanding of writing and debugging tests, identifying logical errors, and ensuring the functionality of the app is well-tested.
- I referred to [W3Schools](https://www.w3schools.com/jsref/met_his_back.asp) for the HTML code used to implement the back button throughout the app.

**Ahmet Taramis:**
- I have used AI to ask it any test scenario I could add which I have missed in the test files I have written. It has recommended me to add the following test scenarios in each file, for which I implemented it in these functions:
  - test_lesson_request_views.py:
  	- test_student_view_unauthenticated()
  	- test_admin_view_unauthenticated()
  	- test_create_request_invalid_data()
  	- test_tutor_cannot_access_admin_view()
  - test_lesson_request_model.py:
  	- test_lesson_request_with_no_description()
  	- test_allocated_lesson_duplicate_occurrence
  - test_lesson_request_form.py:
  	- test_form_with_empty_data()
  	- test_form_with_partial_data()
  	- test_form_tutor_not_selected()

- I have used https://www.w3schools.com/django/ for general help on Django syntax and its tools.
- I have used chatGPT for a deeper understanding of git and how to use the CLI to manage our project.

**Raphael Ahiable**
- I consulted ChatGPT to ensure test classes thoroughly covered views and forms I had written. It was also used to debug these test classes. 

- The following test classes were affected by this:
  - InvoiceViewTests (test_invoice_view.py)
  - InvoiceFormTestCase (test_invoice_form.py)

- For the following test class, ChatGPT was only used for debugging purposes:
  - InvoiceModelTest (test_invoice_model.py)

- I used AI in this project to cement gaps in my knowledge of using the Django framework such as understanding the Django ORM, database and file directory.
- I have used the Django forums (forum.djangoproject.com) for general debugging purposes.
