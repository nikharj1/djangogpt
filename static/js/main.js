const chatBox = 
    document.getElementById('chat-box');
const userInput = 
    document.getElementById('user-input');
const sendButton = 
    document.getElementById('send-button');
const sidebarToggle = 
    document.getElementById('sidebar-toggle');

const sidebar = 
    document.querySelector('.sidebar');




document.addEventListener('DOMContentLoaded', function () {
    const newConversationBtn = 
            document.getElementById('new-conversation-btn');
    const conversationContent = 
            document.querySelector('.conversation-content');
    const sidebarToggle = 
            document.getElementById('sidebar-toggle');
    const sidebarToggle2 = 
            document.getElementById('sidebar-toggle2');
            
    const chatContainer = 
            document.querySelector('.chat-container');
    
    sidebarToggle.addEventListener('click', function () {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('collapsed');

        if (sidebar.classList.contains('collapsed')) {
            chatContainer.style.width = '96%';
            chatContainer.style.marginLeft = '3%';
        } else {
            
            chatContainer.style.marginLeft = '225px';
        }
    });
    sidebarToggle2.addEventListener('click', function () {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('collapsed');

        if (sidebar.classList.contains('collapsed')) {
            chatContainer.style.width = '96%';
            chatContainer.style.marginLeft = '3%';
        } else {
            
            chatContainer.style.marginLeft = '225px';
            sidebar.style.display = "block";
        }
    });
    newConversationBtn.addEventListener('click', function () {
        conversationContent.textContent = "New Conversation Started!";
    });

   
});



// login js 


$(document).ready(function() {
    // Check the initial state of the checkbox and set the mode accordingly
    const modeToggleCheckbox = $('#mode-toggle-checkbox');
    const body = $('body');

    // Function to set the mode
    function setMode() {
        if (modeToggleCheckbox.is(':checked')) {
            body.removeClass('light-mode').addClass('dark-mode');
            $('#mode-icon').html('<i class="fas fa-moon"></i>'); // Dark mode icon
        } else {
            body.removeClass('dark-mode').addClass('light-mode');
            $('#mode-icon').html('<i class="fas fa-sun"></i>'); // Light mode icon
        }
    }

    // Initial mode setup
    setMode();

    // Toggle event
    modeToggleCheckbox.change(function() {
        setMode();
    });
});
