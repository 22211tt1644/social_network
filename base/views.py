from multiprocessing import context
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout,update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from django.views.generic import DetailView,CreateView
from django.contrib.auth.views import PasswordChangeView
from .models import *
from django.urls import reverse_lazy,reverse
from django.views import View
from django.views.generic import ListView,DetailView,CreateView
from .forms import *
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from itertools import chain
from django.db.models import Q, Count
import random
from random import randint
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail


# Create your views here.
@login_required(login_url='signup')
def home(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    all_users = User.objects.all()
    all_posts=Post.objects.all().annotate(total_comments=Count('comments'))
    all_profile=Profile.objects.all()
    count_posts=len(all_posts)
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    posts_with_comments = {}
    for post in all_posts:
        total_comments = post.comments.count()
        posts_with_comments[post.id] = total_comments

    my_user=[user_profile]
    suggestion_users=[]

    for user in all_profile:
        if user not in my_user:
            suggestion_users.append(user)

    random.shuffle(suggestion_users)

    context={
        'user_object':user_object,
        'user_profile':user_profile,
        'all_users':all_users,
        'all_posts':all_posts,
        'all_profile':all_profile,
        'count_posts':count_posts,
        'suggestion_users':suggestion_users,
        'unread_notifications_count': unread_notifications_count,
        'posts_with_comments': posts_with_comments
    }
    return render(request,"base/home.html",context)

class ShowProfilePageView(DetailView):
    model = Profile
    template_name = 'base/Otherprofile.html'

    def get_context_data(self,*args,**kwargs):
        context=super().get_context_data(*args,**kwargs)
        page_user=get_object_or_404(User,id=self.kwargs.get('pk'))
        page_user_profile=get_object_or_404(Profile,id=self.kwargs.get('pk'))
        logged_in_user = self.request.user
        logged_in_user_posts = Post.objects.filter(author=page_user).order_by('-id')


        # Kiểm tra trạng thái kết bạn
        is_friend = page_user_profile.user in logged_in_user.profile.friends.all()
        received_request = FriendRequest.objects.filter(from_user=page_user_profile.user, to_user=logged_in_user).first()
        sent_request = FriendRequest.objects.filter(from_user=logged_in_user, to_user=page_user_profile.user).first()

        # Kiểm tra trạng thái theo dõi
        is_following = FollowersCount.objects.filter(user=page_user_profile.user, follower=logged_in_user).exists()

        # Đếm số lượng người theo dõi và số lượng bạn bè
        follower_count = FollowersCount.objects.filter(user=page_user_profile.user).count()
        following_count = FollowersCount.objects.filter(follower=page_user_profile.user).count()
        friend_count = page_user_profile.friends.count()
        friends = page_user_profile.friends.all()

        # Kiểm tra trạng thái chặn
        is_blocked = BlockList.objects.filter(blocker=logged_in_user, blocked=page_user).exists()
        is_blocking_you = BlockList.objects.filter(blocker=page_user, blocked=logged_in_user).exists()
        blocked_users = BlockList.objects.filter(blocker=logged_in_user)
        blocked_user_list = [block.blocked for block in blocked_users]


        num_posts=len(logged_in_user_posts)
        context["page_user"]=page_user
        context["page_user_profile"]=page_user_profile
        context['logged_in_user_posts']=logged_in_user_posts
        context['num_posts']=num_posts
        context["is_following"] = is_following
        context["is_friend"] = is_friend
        context["received_request"] = received_request
        context["sent_request"] = sent_request
        context["follower_count"] = follower_count
        context["following_count"] = following_count
        context["friend_count"] = friend_count
        context['friend_id'] = page_user_profile.user.id
        context['friends'] = friends
        context['is_blocked'] = is_blocked
        context['is_blocking_you'] = is_blocking_you
        context['blocked_users'] = blocked_user_list

        return context
    
def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=="POST":
        login_username=request.POST.get('username', None)
        user_password=request.POST["password"]
        user = authenticate(request,username=login_username, password = user_password)
        if user is not None:
            auth_login(request, user)
            messages.add_message(request, messages.INFO, 'You have successfully logged in.')
            return redirect('/')

        else:
            messages.add_message(request, messages.INFO, 'Invalid username or password.')
            return render(request,"base/login.html")

    return render(request,"base/login.html")

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST': 
        email=request.POST['email']
        password=request.POST['password']
        username=request.POST['username']
        email=email.rstrip()

        if email == '' or password == '' or username == '':
            messages.error(request,"Please fill all the fields.")
            return render(request,"base/signup.html")
        
        elif User.objects.filter(username=username).exists(): 
            messages.add_message(request, messages.INFO, 'Username already exists.')
            return render(request,"base/signup.html")
        
        elif User.objects.filter(email=email).exists():
            messages.add_message(request, messages.INFO, 'Email already exists.')
            return render(request,"base/signup.html")

        else :
            user = User.objects.create(email=email, username=username, password=make_password(password))
            user.save() 
            auth_login(request, user)    
            messages.add_message(request, messages.INFO, 'You have successfully signed up.')
            return redirect('/create_profile_page')
    else:
        return render(request,"base/signup.html")
    
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('/')

class FriendView(ListView):
    model = Profile
    template_name = 'base/friends.html'
    profiles=Profile.objects.all()
    ordering = ['-id']

    def get_context_data(self,*args,**kwargs):
        context=super(FriendView,self).get_context_data(*args,**kwargs)
        page_user=get_object_or_404(Profile)
        context["page_user"]=page_user
        return context

@login_required
def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        
        if title or image:
            post = Post( author=request.user)
            if title:
                post.title = title
            if image:
                post.image = image
            post.save()
            return redirect('home')
        else:
            return render(request, 'add_post.html', {'error': 'Vui lòng nhập tiêu đề bài viết!'})
    else:
        return render(request, 'home.html')

class CreateProfilePageView(CreateView):
    model = Profile
    form_class=ProfilePageForm
    template_name="base/create_user_profile.html"

    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)

@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        avatar = request.FILES.get('avatar')

        if full_name:
            profile.full_name = full_name
        if bio:
            profile.bio = bio
        if location:
            profile.location = location
        if avatar:
            profile.avatar = avatar

        profile.save()
        return redirect('show_profile_page')

    return render(request, 'base/Otherprofile.html', {'profile': profile})

def edit_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)  # Lấy profile theo pk

    if request.method == 'POST':
        form = ProfilePageForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('show_profile_page', pk=profile.pk)  # Sau khi lưu thành công, chuyển hướng về trang profile
    else:
        form = ProfilePageForm(instance=profile)

    return render(request, 'base/Otherprofile.html', {'form': form, 'profile': profile})

class PasswordsChangeView(PasswordChangeView):
       form_class= PasswordChangingForm
       success_url= reverse_lazy('password_success')

def password_success(request):
    return render(request, 'base/password_success.html', {})

class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'base/add_comment.html'

    def form_valid(self,form):
        form.instance.post_id=self.kwargs['pk']

        post = form.instance.post 
        user = self.request.user  
        sender = user  

        if sender != post.author.user:
            Notification.objects.create(
                user=post.author.user, 
                sender=sender,
                notification_type='comment',
                post=post,
            )
        response = super().form_valid(form)

        # Lấy tất cả comment của bài viết này
        comments = Comment.objects.filter(post=post)

        # Truyền các comment vào context của response để hiển thị trong template
        response.context_data['comments'] = comments
        return response


class LikePost(View):
        def post(self, request, post_id, *args, **kwargs):
            post = Post.objects.get(id = post_id)
            is_like = False

            for like in post.likes.all():
                if like ==request.user:
                    is_like = True
                    break
            
            if not is_like:
                post.likes.add(request.user)

                if post.author != request.user:  # Không gửi thông báo cho chính mình
                    Notification.objects.create(
                        user=post.author,  # Người nhận thông báo
                        sender=request.user,  # Người thích bài viết
                        notification_type='like',
                        post=post,
                    )

            if is_like:
                post.likes.remove(request.user)

            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)

@login_required(login_url='signup')
def search(request):
    query = request.GET.get('q', '').strip()  # Lấy từ khóa tìm kiếm, mặc định là chuỗi rỗng
    profile_results = Profile.objects.filter(
        Q(user__username__icontains=query) | Q(full_name__icontains=query)
    ) if query else []

    # Tìm kiếm trong Post
    post_results = Post.objects.filter(
        Q(title__icontains=query)
    ) if query else []

    context = {
        'query': query,
        'profile_results': profile_results,
        'post_results': post_results,
    }
    return render(request, 'base/search.html', context)

@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        
        if title:
            post.title = title
        if image:
            post.image = image
        
        post.save()
        
        return redirect('home')
    
    return render(request, 'update_post.html', {'post': post})

@login_required(login_url='signup')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/')
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/')
    else:
        return redirect('/')
    
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    
    if request.method == "GET":
        post.delete()
        return redirect('home')
    
    return redirect('home')

def notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'base/notifications.html', {'notifications': notifications})

def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    notification.is_read = True
    notification.save()

    notification.delete()
    return redirect('notifications')

@login_required
def delete_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()

    return redirect('notifications')

# Gửi yêu cầu kết bạn
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    from_user = request.user
    # Kiểm tra xem yêu cầu đã tồn tại chưa
    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return redirect('show_profile_page', pk=user_id)
    # Tạo yêu cầu kết bạn mới
    FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    # Tạo thông báo cho người nhận yêu cầu kết bạn
    Notification.objects.create(
        user=to_user,  # Người nhận thông báo
        sender=from_user,  # Người gửi thông báo
        notification_type='add', 
    )
    return redirect('show_profile_page', pk=user_id)

# Chấp nhận yêu cầu kết bạn
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    # Thêm bạn vào danh sách bạn bè của cả hai người dùng
    from_user_profile = Profile.objects.get(user=friend_request.from_user)
    to_user_profile = Profile.objects.get(user=friend_request.to_user)
    from_user_profile.friends.add(friend_request.to_user)
    to_user_profile.friends.add(friend_request.from_user)
    friend_request.delete()
    # Tạo thông báo cho người gửi người
    Notification.objects.create(
        user=friend_request.from_user, 
        sender=friend_request.to_user,
        notification_type='friend',
    )
    return redirect('show_profile_page', pk=friend_request.from_user.id)

# Hủy yêu cầu kết bạn đã gửi
@login_required
def cancel_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, from_user=request.user)
    to_user_id = friend_request.to_user.id
    friend_request.delete()
    return redirect('show_profile_page', pk=to_user_id)

# Hủy kết bạn
@login_required
def unfriend(request, user_id):
    user_profile = get_object_or_404(Profile, user=request.user)
    friend_profile = get_object_or_404(Profile, user__id=user_id)
    # Xóa bạn khỏi danh sách bạn bè của cả hai
    user_profile.friends.remove(friend_profile.user)
    friend_profile.friends.remove(request.user)
    # Tạo thông báo cho cả hai người khi hủy kết bạn
    return redirect('show_profile_page', pk=user_id)

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    # Kiểm tra xem đã theo dõi chưa
    if not FollowersCount.objects.filter(user=user_to_follow, follower=request.user).exists():
        FollowersCount.objects.create(user=user_to_follow, follower=request.user)

        # Tạo thông báo cho người được theo dõi
        Notification.objects.create(
            user=user_to_follow,  # Người nhận thông báo
            sender=request.user,  # Người gửi thông báo
            notification_type='follow'
        )
    return redirect('show_profile_page', pk=user_id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    # Kiểm tra xem có đang theo dõi không
    FollowersCount.objects.filter(user=user_to_unfollow, follower=request.user).delete()
    return redirect('show_profile_page', pk=user_id)

@login_required
def chat_view(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    messages = Message.objects.filter(
        sender=request.user, receiver=friend
    ) | Message.objects.filter(
        sender=friend, receiver=request.user
    )
    messages = messages.order_by("timestamp")  

    Message.objects.filter(sender=friend, receiver=request.user, is_read=False).update(is_read=True)


    if request.method == "POST":
        content = request.POST.get("content","").strip()
        if content:
            Message.objects.create(sender=request.user, receiver=friend, content=content)
        return redirect("chat_view", friend_id=friend.id)

    return render(request, "base/chat.html", {
        "friend": friend,
        "messages": messages,
    })

@login_required
def message_list(request):

    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')

    friends = []
    for convo in conversations:
        if convo.sender == request.user:
            friend = convo.receiver
        else:
            friend = convo.sender
        friends.append(friend)

    friends = list(set(friends))

    return render(request, 'base/chat_list.html', {'friends': friends})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')  # ID của bình luận cha (nếu có)
        if content:
            parent_comment = Comment.objects.filter(id=parent_id).first() if parent_id else None
            new_comment = Comment.objects.create(post=post, user=request.user, content=content, parent=parent_comment)

            if parent_comment:
                if parent_comment.user != request.user:
                    Notification.objects.create(
                        user=parent_comment.user,
                        sender=request.user,
                        notification_type='reply',
                        post=post,
                        comment=new_comment
                    )
            else:
                if post.author != request.user: 
                    Notification.objects.create(
                        user=post.author, 
                        sender=request.user,
                        notification_type='comment',
                        post=post,
                        comment=new_comment
                    )
        return redirect('post_detail', post_id = post_id)

    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')  # Chỉ lấy bình luận chính
    return render(request, 'base/post_detail.html', {'post': post, 'comments': comments,})

def send_otp(request):
    if request.method == 'POST':
        form = RequestOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                # Tạo mã OTP
                otp_code = str(randint(100000, 999999))

                # Lưu mã OTP vào database
                OTP.objects.create(user=user, code=otp_code)

                # Gửi mã OTP qua email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp_code}',
                    'your_email@gmail.com',
                    [email],
                )
                return redirect('verify_otp')  # Chuyển đến bước xác minh
            else:
                form.add_error('email', 'Email không tồn tại.')
    else:
        form = RequestOTPForm()
    return render(request, 'base/send_otp.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']
            otp_entry = OTP.objects.filter(code=otp_code, is_used=False).first()

            if otp_entry and (now() - otp_entry.created_at < timedelta(minutes=10)):
                # Cập nhật mật khẩu người dùng
                user = otp_entry.user
                user.password = make_password(new_password)
                user.save()

                # Đánh dấu OTP là đã dùng
                otp_entry.is_used = True
                otp_entry.save()

                return redirect('login')  # Chuyển đến trang đăng nhập
            else:
                form.add_error('otp', 'Mã OTP không hợp lệ hoặc đã hết hạn.')
    else:
        form = VerifyOTPForm()
    return render(request, 'base/verify_otp.html', {'form': form})

def share_post(request, post_id):
    # Lấy bài viết gốc
    original_post = get_object_or_404(Post, id=post_id)

    # Tạo bài viết mới dựa trên bài viết gốc
    shared_post = Post.objects.create(
        author= request.user,  # Người đang chia sẻ
        title=original_post.title,  # Nội dung bài viết gốc
        image=original_post.image,  # Ảnh từ bài viết gốc
        shared_from=original_post  # Gán bài viết gốc
    )

    messages.success(request, "Bạn đã chia sẻ bài viết thành công!")
    return redirect('home')

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        group_image = request.FILES.get('image')
        if group_name:
            group = Group.objects.create(name=group_name, creator=request.user, image=group_image)
            # Thêm người tạo vào nhóm làm thành viên
            GroupMember.objects.create(group=group, user=request.user)
            messages.success(request, f"Bạn đã tạo nhóm {group_name} thành công!")
            # Sau khi tạo nhóm, chuyển hướng đến trang mời bạn bè vào nhóm
            return redirect('invite_to_group', group_id=group.id)
    return render(request, 'base/create_group.html')

# View mời bạn bè vào nhóm
@login_required
def invite_to_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    # Lấy danh sách bạn bè của người dùng hiện tại
    all_friends = request.user.profile.friends.all()  # Giả định rằng bạn có field friends trong model Profile
    group_members = group.members.values_list('user', flat=True)  # Lấy danh sách ID thành viên nhóm
    friends_to_invite = all_friends.exclude(id__in=group_members)  # Loại bỏ bạn bè đã là thành viên nhóm

    if request.method == 'POST':
        user_ids = request.POST.getlist('user_ids')  # Lấy danh sách ID bạn bè được chọn
        invited_users = User.objects.filter(id__in=user_ids)

        for invited_user in invited_users:
            # Thêm thành viên vào nhóm
            GroupMember.objects.create(group=group, user=invited_user)
            messages.success(request, f"Bạn đã mời {invited_user.username} vào nhóm.")

        return redirect('group_detail', group_id=group.id)

    return render(request, 'base/invite_to_group.html', {'group': group, 'friends': friends_to_invite})

# View chi tiết nhóm
@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    messages_group = group.messages.all()  # Các tin nhắn trong nhóm
    members = group.members.all()  # Thành viên trong nhóm
    return render(request, 'base/group_detail.html', {'group': group, 'messages': messages_group, 'members': members})

# View gửi tin nhắn vào nhóm
@login_required
def send_message(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        message_content = request.POST.get('content')
        if message_content:
            MessageGroup.objects.create(group=group, user=request.user, content=message_content)
            messages.success(request, "Tin nhắn của bạn đã được gửi.")
    return redirect('group_detail', group_id=group.id)

@login_required
def list_groups(request):
    # Lấy tất cả các nhóm mà người dùng hiện tại là thành viên
    user_groups = Group.objects.filter(members__user=request.user).distinct()
    
    return render(request, 'base/list_groups.html', {'user_groups': user_groups})

@login_required
def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        group_name = request.POST.get('name')  # Lấy tên nhóm từ form
        group_image = request.FILES.get('image')  # Lấy ảnh từ form

        if group_name:
            group.name = group_name
        if group_image:
            group.image = group_image

        group.save()  # Lưu thay đổi
        messages.success(request, "Thông tin nhóm đã được cập nhật.")
        return redirect('group_detail', group_id=group.id)

    return render(request, 'base/group_detail.html', {'group': group})

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    member = GroupMember.objects.filter(group=group, user=request.user).first()

    if not member:
        messages.error(request, "Bạn không phải là thành viên của nhóm này.")
        return redirect('group_detail', group_id=group_id)

    # Nếu là creator và nhóm chỉ có một thành viên
    if group.creator == request.user and group.members.count() == 1:
        group.delete()
        messages.success(request, "Bạn đã rời nhóm và nhóm đã bị xóa do không còn thành viên.")
        return redirect('home')

    # Nếu là creator, chuyển quyền quản lý cho một thành viên khác
    if group.creator == request.user:
        new_creator = group.members.exclude(user=request.user).first()
        if new_creator:
            group.creator = new_creator.user
            group.save()
            messages.success(request, f"Bạn đã rời nhóm. Quyền quản lý đã được chuyển cho {new_creator.user.username}.")
        else:
            group.delete()  # Nếu không còn ai khác, xóa nhóm
            messages.success(request, "Bạn đã rời nhóm và nhóm đã bị xóa do không còn thành viên.")
            return redirect('home')

    # Xóa thành viên khỏi nhóm
    member.delete()
    messages.success(request, "Bạn đã rời khỏi nhóm.")
    return redirect('home')

def toggle_block(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        friend = get_object_or_404(User, id=friend_id)
        
        block_entry = BlockList.objects.filter(blocker=request.user, blocked=friend)
        if block_entry.exists():
            # Nếu đã chặn, bỏ chặn
            block_entry.delete()
        else:
            # Nếu chưa chặn, thực hiện chặn
            BlockList.objects.get_or_create(blocker=request.user, blocked=friend)
        
        # Chuyển hướng lại trang profile
        return redirect('show_profile_page', pk=friend.id)
    return redirect('home')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user

        user.delete()
        logout(request)

        return redirect('home')
    return render(request, 'base/delete_user.html')

def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Kiểm tra nếu người dùng đã like bình luận này rồi
    if not CommentLike.objects.filter(user=request.user, comment=comment).exists():
        # Nếu chưa like, tạo một like mới
        CommentLike.objects.create(user=request.user, comment=comment)
    else:
        # Nếu đã like, xóa like
        CommentLike.objects.filter(user=request.user, comment=comment).delete()

    likes_count = comment.likes.count()

    # Chuyển hướng về trang bài viết (hoặc trang trước đó)
    return redirect(comment.get_absolute_url())

def delete_comment(request, comment_id):
    # Lấy bình luận theo ID
    comment = get_object_or_404(Comment, id=comment_id)

    # Kiểm tra nếu người dùng là tác giả của bình luận này hoặc chủ bài viết
    if comment.user == request.user or comment.post.author == request.user:
        # Xóa bình luận nếu người dùng là tác giả hoặc chủ bài viết
        comment.delete()

    # Chuyển hướng về trang chi tiết bài viết có bình luận
    return redirect(comment.get_absolute_url())