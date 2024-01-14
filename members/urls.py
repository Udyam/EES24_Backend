from django.urls import path, include
from members.views import (
	UserRegistrationAPIView,
	UserLoginAPIView,
	UserViewAPI,
	UserLogoutViewAPI,
	ExportImportExcel,
	BroadCastViewAPI,

	VerifyEmailView,
	ForgotPassword,
	ChangePassword
)


urlpatterns = [
	path('user/register/', UserRegistrationAPIView.as_view()),
	path('user/login/', UserLoginAPIView.as_view()),
	path('user/', UserViewAPI.as_view()),
	path('user/logout/', UserLogoutViewAPI.as_view()),
	path('excel/', ExportImportExcel.as_view()),
	path('broadcast/', BroadCastViewAPI.as_view()),
	path('user/verify',VerifyEmailView.as_view(),name="user-verify"),
	path('user/forgot-password', ForgotPassword.as_view(), name="forgot"),
	path('user/change-password', ChangePassword.as_view(), name="change-password")
]

