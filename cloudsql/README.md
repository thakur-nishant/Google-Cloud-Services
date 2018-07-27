Programming Assignment 5
 Data Visualization

Description:
 It is difficult to find meaning in large volumes of “textual” output, most users
 prefer pictures: graphs, pie charts, etc.
 Various mechanisms for visualizing data within a browser, which are “light weight”
 and require no plugins, or additional (local) downloads support showing results
 which are easy to read and understand.
 (Free) supporting tools and libraries include:
 Javascript:
 d3js.org
 InfoVis: philogb.github.io/jit/demos.html
 js.cytoscape.org
 Other:
 developers.google.com/chart/
 www.highcharts.com (HTML5)
 https://www.slant.co/options/10577/alternatives/~d3-js-alternatives or
 https://alternativeto.net/software/d3-js/
 (use only one of the free javascript ones)

 Your assignment is to visualize and display the results from your previous assignments
 within a browser, allow a user to select intervals or attributes in a data set, show
 results as a pie chart, a histogram, or a scatter or point chart (possibly connected:
 a line).

 Using those SQL tables to do queries, rather than display the results as text,
 display as an image (a picture).
For example:
 For Earthquakes:
 For a 7 day period show quakes in magnitude intervals: less than 2,
 2 to 2.5, 2.5 to 3.0, up to 6.0 to 6.5
 Show this as a horizontal barchart as well as a pie chart
 For the Titanic data:
 On a pie chart show percent female survivor and not for 1st,2nd and 3rd class
 passengers
 On a bar chart show numbers of male survivors and not for 1st,2nd and 3rd class
 passengers
 Using ML clustering, for 8 clusters in Titanic data, based on age
 and fare price show centroids on point (scatter) chart.
 Users of this service will interact with your service through web page
 interfaces, all processing and web service hosting is (of course) cloud based. 


# Python Google Cloud SQL instructions for Google App Engine Flexible

[![Open in Cloud Shell][shell_img]][shell_link]

[shell_img]: http://gstatic.com/cloudssh/images/open-btn.png
[shell_link]: https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/GoogleCloudPlatform/python-docs-samples&page=editor&open_in_editor=appengine/flexible/cloudsql/README.md

This sample demonstrates how to use [Google Cloud SQL](https://cloud.google.com/sql/) (or any other SQL server) on [Google App Engine Flexible](https://cloud.google.com/appengine).

## Setup

Before you can run or deploy the sample, you will need to do the following:

1. Create a [Second Generation Cloud SQL](https://cloud.google.com/sql/docs/create-instance) instance. You can do this from the [Cloud Console](https://console.developers.google.com) or via the [Cloud SDK](https://cloud.google.com/sdk). To create it via the SDK use the following command:

        $ gcloud sql instances create YOUR_INSTANCE_NAME \
            --activation-policy=ALWAYS \
            --tier=db-n1-standard-1

1. Set the root password on your Cloud SQL instance:

        $ gcloud sql instances set-root-password YOUR_INSTANCE_NAME --password YOUR_INSTANCE_ROOT_PASSWORD

1. Create a [Service Account](https://cloud.google.com/sql/docs/external#createServiceAccount) for your project. You'll use this service account to connect to your Cloud SQL instance locally.

1. Download the [Cloud SQL Proxy](https://cloud.google.com/sql/docs/sql-proxy).

1. Run the proxy to allow connecting to your instance from your machine.

    $ cloud_sql_proxy \
        -dir /tmp/cloudsql \
        -instances=YOUR_PROJECT_ID:us-central1:YOUR_INSTANCE_NAME=tcp:3306 \
        -credential_file=PATH_TO_YOUR_SERVICE_ACCOUNT_JSON

1. Use the MySQL command line tools (or a management tool of your choice) to create a [new user](https://cloud.google.com/sql/docs/create-user) and [database](https://cloud.google.com/sql/docs/create-database) for your application:

    $ mysql -h 127.0.0.1 -u root -p
    mysql> create database YOUR_DATABASE;
    mysql> create user 'YOUR_USER'@'%' identified by 'PASSWORD';
    mysql> grant all on YOUR_DATABASE.* to 'YOUR_USER'@'%';

1. Set the connection string environment variable. This allows the app to connect to your Cloud SQL instance through the proxy:

    export SQLALCHEMY_DATABASE_URI=mysql+pymysql://USER:PASSWORD@127.0.0.1/YOUR_DATABASE

1. Run ``create_tables.py`` to ensure that the database is properly configured and to create the tables needed for the sample.

1. Update the connection string in ``app.yaml`` with your configuration values. These values are used when the application is deployed.

## Running locally

Refer to the [top-level README](../README.md) for instructions on running and deploying.

It's recommended to follow the instructions above to run the Cloud SQL proxy. You will need to set the following environment variables via your shell before running the sample:

    $ export SQLALCHEMY_DATABASE_URI=[your connection string]
    $ python main.py
