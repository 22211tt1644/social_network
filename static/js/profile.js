function openEditProfilePopup() {
    document.getElementById("editProfilePopup").style.display = "flex";
}

function openEditGroupPopup() {
    document.getElementById("editGroupPopup").style.display = "flex";
}

// Đóng popup khi nhấn ra ngoài nội dung
window.onclick = function(event) {
    const popup = document.getElementById("editProfilePopup");
    const group = document.getElementById("editGroupPopup")
    const popupContent = document.querySelector(".popup-content-profile");
    const popupGroup = document.querySelector(".popup-content-group");
    
    // Kiểm tra nếu nhấn ra ngoài nội dung popup
    if (event.target === popup && !popupContent.contains(event.target)) {
        popup.style.display = "none";
    }

    if (event.target === group && !popupGroup.contains(event.target)) {
        group.style.display = "none";
    }
    
    
}

function triggerFileInput() {
    document.getElementById("file-input").click();
}

function triggerFileMess() {
    document.getElementById("file-input-mess").click();
}

// Hiển thị ảnh đã chọn ngay trên giao diện
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
        // Đặt ảnh vừa tải lên vào thẻ img
        document.getElementById("profile-image").src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);  // Đọc ảnh đã chọn
}

function openUnfriendPopup() {
    document.getElementById("UnfriendPopup").style.display = "flex";
}

function closeUnfriendPopup() {
    document.getElementById("UnfriendPopup").style.display = "none";
}

function openUnfollowPopup() {
    document.getElementById("UnfollowPopup").style.display = "flex";
}

function closeUnfollowPopup() {
    document.getElementById("UnfollowPopup").style.display = "none";
}

function openListFriendPopup() {
    document.getElementById("popupFriend").style.display = "flex";
}
function closeListFriendPopup() {
    document.getElementById("popupFriend").style.display = "none";
}

function openBlockFriendPopup() {
    document.getElementById("popupBlock").style.display = "flex";
}
function closeBlockFriendPopup() {
    document.getElementById("popupBlock").style.display = "none";
}

function openLeavePopup() {
    document.getElementById("groupleave").style.display = "flex";
}
function closeLeavePopup() {
    document.getElementById("groupleave").style.display = "none";
}