const cards=document.querySelectorAll(".info-card");

cards.forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.style.boxShadow="0 0 25px rgba(139,92,246,.5)";

});

card.addEventListener("mouseleave",()=>{

card.style.boxShadow="none";

});

});