from django.urls import path
from abnormaldetect import views
from abnormaldetect.models import LogMessage

from django.contrib import admin
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

home_list_view = views.HomeListView.as_view(
    queryset=LogMessage.objects.order_by("-log_date")[:5],  # :5 limits the results to the five most recent
    context_object_name="message_list",
    template_name="abnormaldetect/logview.html",
)

urlpatterns = [
    #User mode version
    path("", views.base, name="base"),
    path("userindex/", views.userindex, name="userindex"),
    path("userdatacheck/", views.userdatacheck, name="userdatacheck"),
    path("userdatacheckdetail/<str:refyear>/<str:refarea>/<str:reflinkid>/", views.userdatacheckdetail, name="userdatacheckdetail"),
    path("userreconcile/<slug:reflinkid>/", views.userreconcile, name="userreconcile"),
    path("userkriset/", views.userkriset, name="userkriset"),
    path("userprediction/", views.userprediction, name="userprediction"),
    path("userinquiry/", views.userinquiry, name="userinquiry"),
    path("userpredictversion/<slug:reflinkid>/", views.userpredictversion, name="userpredictversion"),
    path("userfrauditem/<slug:reflinkid>/", views.userfrauditem, name="userfrauditem"),
    path("userriskprofile/<slug:reflinkid>/", views.userriskprofile, name="userriskprofile"),
    path("usermodel/<slug:reflinkid>/", views.usermodel, name="usermodel"),
    path("userlogisticmodel/<slug:reflinkid>/", views.userlogisticmodel, name="userlogisticmodel"),
    path("userdecisiontreemodel/<slug:reflinkid>/", views.userdecisiontreemodel, name="userdecisiontreemodel"),
    path("userrandomforestmodel/<slug:reflinkid>/", views.userrandomforestmodel, name="userrandomforestmodel"),

    path('signin/',auth_views.LoginView.as_view(template_name="abnormaldetect/signin.html"), name="signin"),
    
    #Previous admin mode version
    path("home/", views.home, name="home"),
    path("log/", home_list_view, name="log"),
    path("taskparameter/", views.taskparameter, name="taskparameter"),
    path("taskdata/", views.taskdata, name="taskdata"),
    path("taskmodelling/", views.taskmodelling, name="taskmodelling"),
    path("taskpreprocessing/", views.taskpreprocessing, name="taskpreprocessing"),
    path("tasklabelling/", views.tasklabelling, name="tasklabelling"),
    path("taskclassification/", views.taskclassification, name="taskclassification"),
    path("tasksubmit/", views.tasksubmit, name="tasksubmit"),
    path("taskcommand/", views.taskcommand, name="taskcommand"),
    path("taskETL/", views.taskETL, name="taskETL"),
    path("tasklog/", views.tasklog, name="tasklog"),
    path("taskquery/", views.taskquery, name="taskquery"),
    path("frauditem/<slug:reflinkid>/", views.frauditem, name="frauditem"),
    path("riskprofile/<slug:reflinkid>/", views.riskprofile, name="riskprofile"),
    path("reconcile/<slug:reflinkid>/", views.reconcile, name="reconcile"),
    path("predictversion/<slug:reflinkid>/", views.predictversion, name="predictversion"),
    path("logisticmodel/<slug:reflinkid>/", views.logisticmodel, name="logisticmodel"),
    path("decisiontreemodel/<slug:reflinkid>/", views.decisiontreemodel, name="decisiontreemodel"),
    path("randomforestmodel/<slug:reflinkid>/", views.randomforestmodel, name="randomforestmodel"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('login/',auth_views.LoginView.as_view(template_name="abnormaldetect/login.html"), name="login"),
    path("about/", views.about, name="about"),
    path("help/", views.help, name="help"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)