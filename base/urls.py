from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateProfilePageView,PasswordsChangeView,FriendView,AddCommentView,ShowProfilePageView
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home,name='home'),
    path('login/', views.login,name='login'),
    path('logout/', views.logout,name='logout'),
    path('delete/', views.delete_account,name='delete_account'),
    path('signup/', views.signup,name='signup'),
    path('<int:pk>/edit_profile_page/',views.edit_profile,name='edit_profile_page'),
    path('<int:pk>/profile/',ShowProfilePageView.as_view(),name='show_profile_page'),
    path('create_profile_page/',CreateProfilePageView.as_view(),name='create_profile_page'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('add_post/',views.add_post,name="add_post"),
    path('post/<int:post_id>/update/', views.update_post, name='update_post'),
    path('password/',PasswordsChangeView.as_view(template_name='base/change-password.html')),
    path('password_success/', views.password_success, name="password_success"),
    path('friends/',FriendView.as_view(),name='friends'),
    path('like-post/<int:post_id>',views.LikePost.as_view(),name='like_post'),
    path('search',views.search,name='search'),
    path('follow',views.follow,name='follow'),
    path('notifications/',views.notifications, name ='notifications'),
    path('notification/<int:notification_id>/mark_as_read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('delete_all_notifications/', views.delete_all_notifications, name='delete_all_notifications'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('cancel_friend_request/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('unfriend/<int:user_id>/', views.unfriend, name='unfriend'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path("chat/<int:friend_id>/", views.chat_view, name="chat_view"),
    path('messages/', views.message_list, name='chat_list'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('share/<int:post_id>/', views.share_post, name='share_post'),
    path('search/', views.search, name='search'),
    path('create_group/', views.create_group, name='create_group'),
    path('group/<int:group_id>/invite/', views.invite_to_group, name='invite_to_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/send_message/', views.send_message, name='send_message'),
    path('groups/', views.list_groups, name='list_groups'),
    path('group/<int:group_id>/update/', views.update_group, name='update_group'),
    path('group/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('block-friend/', views.toggle_block, name='toggle_block'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)