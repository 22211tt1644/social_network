let selectedPostId = null;

function toggleMenu() {
    const menu = document.getElementById("popupMenu");
    menu.style.display = menu.style.display === "none" || menu.style.display === "" ? "block" : "none";
    menu.classList.toggle("show");
}

// Đóng menu khi click ra ngoài
window.onclick = function (event) {
    const menu = document.getElementById("popupMenu");
    const link = document.querySelector(".menu-link");
    if (!menu.contains(event.target) && !link.contains(event.target)) {
        menu.style.display = "none";
        menu.classList.remove("show");
    }
}
// Hàm ẩn/hiện form và overlay
function toggleForm() {
    const form = document.querySelector('.popup-gd');
    const overlay = document.querySelector('.overlay');
    form.style.display = form.style.display === 'flex' ? 'none' : 'flex';
    overlay.style.display = overlay.style.display === 'block' ? 'none' : 'block';
}
const themeContainer = document.getElementById("theme-container");
const toggleInterfaceBtn = document.getElementById("toggle-interface");


/* Đăng bài */
function openPopup() {
    document.querySelector(".home").classList.add('no-scroll');
    document.getElementById("popup").style.display = "flex";
}

function checkInput() {
    var title = document.getElementById("title").value.trim();
    var fileInput = document.getElementById("file-input").files.length;
    var submitBtn = document.getElementById("submit-btn");

    // Kiểm tra nếu trường tiêu đề không trống và có file ảnh được chọn
    if (title.length !== "" || fileInput > 0) {
        submitBtn.disabled = false;  // Kích hoạt nút nếu có dữ liệu
    } else {
        submitBtn.disabled = true;   // Giữ nút ở trạng thái disabled nếu không có dữ liệu
    }
}
// Đóng popup
function closePopup() {
    document.getElementById("popup").style.display = "none";
}

window.onclick = function (event) {
    var popup = document.getElementById("popup");
    var popupContent = document.querySelector(".popup-content");

    if (event.target == popup) {
        closePopup();
    }
}


// Đóng popup-chinhsua khi nhấn ngoài khu vực popup
window.onclick = function (event) {
    const popup = document.getElementById(`popup-chinhsua-${selectedPostId}`);
    if (event.target !== popup && !popup.contains(event.target) && event.target.className !== 'bx bx-dots-horizontal-rounded post-icon post-them') {
        popup.style.display = "none";
        selectedPostId = null;
    }
}


function togglePopupChinhsua(event, postId) { 
    // Đóng tất cả popup trước khi mở popup mới
    document.querySelector(".home").classList.add('no-scroll');
    document.querySelectorAll(".popup-chinhsua").forEach(popup => {
        popup.style.display = "none";
    });

    // Mở popup của bài viết đã chọn
    const popup = document.getElementById(`popup-chinhsua-${postId}`);
    if (popup) {
        popup.style.display = "block";
        const iconRect = event.target.getBoundingClientRect();
        popup.style.top = `${iconRect.bottom + window.scrollY}px`;
        popup.style.left = `${iconRect.left + window.scrollX}px`;
        selectedPostId = postId;
    }
}

function openDeletePopup(postId) {
    document.querySelector(".home").classList.add('no-scroll');
    selectedPostId = postId;
    document.getElementById("deleteConfirmationPopup").style.display = "flex";
    document.getElementById(`popup-chinhsua-${postId}`).style.display = "none";
}

function closeDeletePopup() {
    document.getElementById("deleteConfirmationPopup").style.display = "none";
}

function openUpdatePopup(postId) {
    document.querySelector(".home").classList.add('no-scroll');
    selectedPostId = postId;
    const popup = document.getElementById("popupUpdate");

    popup.querySelector("form").action = `/post/${postId}/update/`;
    const postTitle = document.getElementById(`post-title-${postId}`).innerText;
    document.getElementById("title-update").value = postTitle;
    const postImage = document.getElementById(`post-image-${postId}`);
    if (postImage && postImage.src) {
        document.getElementById("image-update-old").src = postImage.src;
        document.getElementById("image-update-old").style.display = "block";
    } else {
        // Nếu không có ảnh, ẩn ảnh cũ hoặc xử lý theo yêu cầu
        document.getElementById("image-update-old").style.display = "none"; // Ẩn ảnh cũ
    }
    document.getElementById("popupUpdate").style.display = "flex";
    document.getElementById(`popup-chinhsua-${postId}`).style.display = "none";
}

function closeUpdatePopup() {
    document.getElementById("popupUpdate").style.display = "none";
}

function confirmDelete() {
    if (selectedPostId) {
        window.location.href = `/post/${selectedPostId}/delete/`;
    }
}

function previewImage(event) {
    const file = event.target.files[0];
    const preview = document.getElementById("image-preview");

    if (file) {
        // Tạo một đối tượng URL từ file đã chọn
        const reader = new FileReader();

        reader.onload = function (e) {
            // Hiển thị ảnh lên trong phần preview
            preview.src = e.target.result;
            preview.style.display = "block"; // Hiển thị ảnh
        }

        reader.readAsDataURL(file); // Đọc file ảnh đã chọn
    } else {
        preview.style.display = "none"; // Nếu không chọn ảnh thì ẩn đi
    }
}

function previewImageUpdate(event) {
    const file = event.target.files[0];
    const newImagePreview = document.getElementById("new-image-preview");
    const oldImagePreview = document.getElementById("image-update-old");

    if (file) {
        // Nếu có ảnh mới, ẩn ảnh cũ và hiển thị ảnh mới
        const reader = new FileReader();

        reader.onload = function (e) {
            // Hiển thị ảnh mới
            newImagePreview.src = e.target.result;
            newImagePreview.style.display = "block"; // Hiển thị ảnh mới

            // Ẩn ảnh cũ nếu có ảnh mới
            if (oldImagePreview) {
                oldImagePreview.style.display = "none";
            }
        }

        reader.readAsDataURL(file); // Đọc file ảnh đã chọn
    } else {
        // Nếu không chọn ảnh, ẩn ảnh mới và hiển thị ảnh cũ nếu có
        newImagePreview.style.display = "none";
        if (oldImagePreview) {
            oldImagePreview.style.display = "block";
        }
    }
}

function openCommentPopup() {
    document.getElementById("popupComment").style.display = "flex";
}

function closeCommentPopup() {
    document.getElementById("popupComment").style.display = "none";
}

function toggleReplyForm(commentId) {
    var form = document.getElementById('reply-form-' + commentId);
    if (form.style.display === 'none') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

function validateForm() {
    const title = document.getElementById("title").value.trim();
    const fileInput = document.getElementById("file-input").files.length;

    // Kích hoạt nút nếu có title hoặc file được chọn
    const submitButton = document.getElementById("submit-btn");
    if (title || fileInput > 0) {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

function openDeleteAccountPopup() {
    document.getElementById("deleteAccountPopup").style.display = "flex";
}
function closeDeleteAccountPopup() {
    document.getElementById("deleteAccountPopup").style.display = "none";
}