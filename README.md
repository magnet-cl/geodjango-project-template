# geodjango-project-template

A template for a Django project. It's simply project that was created with django 1.6.2
project with a lot of tweaks, usually things that we do in all projects.

## Requirements
* Python 2.7: This project was tested using python 2.7
* Node: This project uses node for bower, less and jade.

## Get the code
Create a new repository in github for your django project.
Clone your repository into your computer.
Add the django-project-template github repo as a remote repository:
* `git remote add template
  git@github.com:magnet-cl/django-project-template.git`
Pull the code from the project template
* `git pull template master` (there may be conflicts with your README.md file,
  fix them and continue)
Push to your own repo
* `git push origin master`
Now you have your own django project in your repository


## Quickstart

For a quick start, run 

* `./quickstart.sh`

It should install all the dependencies you need to start the project. Then you
need to Configure your database settings in project/local_settings.py.

You can reset the database with:

* `./reset.sh`

## Features

### Bootstrap 3 integration
Since We have been using bootstrap 3 for all our project, we made that all
templates in the project are written for bootstrap 3. 

Also, the project compiles the source code for bootstrap 3 from less. This is
done so a rapid customization can be made of your site's style. The source
code for less is in `base/static/css/bootstrap/`

### Bootstrap 3 admin
bootstrap-admin==0.3.0
Since We have been using bootstrap 3 for all our project, we made that all
templates in the project are written for bootstrap 3. 
* bootstrap admin
* captcha login
* bower integration

### Base: 
Base is the first application of this project template.

* Custom models:
    * BaseModel: An abstract django model that all your models should inherit
      from. Contains the following methods
       * `update(self, *kwargs)`: updates in the database only the fields you
         pass in the keyword arguments
    * User: Custom user model that inherits form
      django.contrib.auth.models.User. This enables easy customization like
      adding new fieds or new methods. 
       * Simple email system to send templated emails.
       * Custom Backend for email authentication instead of username
         authentication
* Fixtures: Fixtures with an admin user
* Admin: A basic configuration for the admin

### Fabric
It includes basic fabric tasks. These tasks are described later.

## Fabric tasks

In order to use fabric to deploy a gunicorn+nginx configuration you must set
the following variables at `fabfile/config.py`:
* `env.server_root_dir`: Remote path of deployment.
* `env.server_git_url`: Your git repository.
* `env.server_domain`: Server domain of target server. (optional)
* `env.hosts`: Default host used by fabric. (optional)

and add a private ssh key file (id_rsa) to `fabfile/templates` named
`ssh_key`. This file will be put in the remote server as the default ssh key
for the remote user.

To get a list of the available tasks run: `fab -l`. 

Make sure to run the following task before any other task in any of the these
formats:
* `fab config.set_host`: Uses the host specified in `env.hosts` and `magnet`
  as user.
* `fab config.set_host:examplehost`: Manually specify host.
* `fab config.set_host:examplehost,user`: Manually specify host and user.
