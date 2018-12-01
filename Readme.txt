Before using the system:
1.) Create a superuser for the database.
1.) Go to /admin/ page and login as the superuser.
2.) Create 4 Group instances with 'Clinic Manager', 'Warehouse Personnel', 'Dispatcher' and 'Admin' as Group names
3.) Go to superuser's User instance and add 'Admin' group to it.
4.) Create an Account instance with the same information(username, password(not the hashed one), first name, last name and email) as the Djano superuser's User instance. 
	Set role as 'Admin'. Leave worklocation and token blank.
5.) Log out and go to /login/ page.
6.) End

Registration:
For Admin:
1.) Login as Admin role at /login/.
2.) Submits email, role and/or location of the requesting user.
3.) Done

For User:
1.) Go to /register/
2.) Submit token.
3.) Fill in and submit required information.
4.) Go to /login/ and use the system.
5.) Done
