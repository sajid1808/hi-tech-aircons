/* ==========================================================================
   HI-TECH AIRCONS - PREMIUM INTERACTIONS SCRIPTS (WITH DB & BRAND SHOWCASE)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // Load and apply website config settings dynamically
    async function loadWebsiteConfig() {
        try {
            const response = await fetch('/api/config');
            if (!response.ok) return;
            const config = await response.json();
            
            // Apply config to elements
            const taglineHeader = document.getElementById('configTaglineHeader');
            if (taglineHeader) taglineHeader.innerText = config.tagline;

            const taglineFooter = document.getElementById('configTaglineFooter');
            if (taglineFooter) taglineFooter.innerText = config.tagline;

            const taglineHero = document.getElementById('configTaglineHero');
            if (taglineHero) taglineHero.innerText = config.tagline;

            const gstin = document.getElementById('configGstin');
            if (gstin) gstin.innerText = `GSTIN: ${config.gstin}`;

            const gstinFooter = document.getElementById('configGstinFooter');
            if (gstinFooter) gstinFooter.innerText = `GSTIN: ${config.gstin}`;

            const contactAddress = document.getElementById('configContactAddress');
            if (contactAddress) contactAddress.innerHTML = config.address.replace(/,\s*/g, ',<br>');

            const footerAddress = document.getElementById('configFooterAddress');
            if (footerAddress) footerAddress.innerText = config.address;

            // Phones
            const contactPhone1 = document.getElementById('configContactPhone1');
            if (contactPhone1) {
                contactPhone1.href = `tel:${config.phone1.replace(/\s+/g, '')}`;
                contactPhone1.innerText = config.phone1;
            }
            const contactPhone2 = document.getElementById('configContactPhone2');
            if (contactPhone2) {
                contactPhone2.href = `tel:${config.phone2.replace(/\s+/g, '')}`;
                contactPhone2.innerText = config.phone2;
            }

            const footerPhones = document.getElementById('configFooterPhones');
            if (footerPhones) {
                footerPhones.innerHTML = `${config.phone1}<br>${config.phone2}`;
            }

            // Emails
            const contactEmail = document.getElementById('configContactEmail');
            if (contactEmail) {
                contactEmail.href = `mailto:${config.email}`;
                contactEmail.innerText = config.email;
            }
            const footerEmail = document.getElementById('configFooterEmail');
            if (footerEmail) footerEmail.innerText = config.email;

            // Copyright
            const copyright = document.getElementById('configCopyright');
            if (copyright) copyright.innerHTML = `&copy; ${config.copyright_year} HI-TECH AIRCONS. All Rights Reserved. Designed with premium cooling engineering.`;

            // Founder
            const ownerTitle = document.getElementById('configOwnerTitle');
            if (ownerTitle) ownerTitle.innerText = config.owner_title;

            const ownerName = document.getElementById('configOwnerName');
            if (ownerName) ownerName.innerText = config.owner_name;

            const ownerQuote = document.getElementById('configOwnerQuote');
            if (ownerQuote) ownerQuote.innerText = `"${config.owner_quote.replace(/^"|"$/g, '')}"`;

            const ownerSignName = document.getElementById('configOwnerSignName');
            if (ownerSignName) ownerSignName.innerText = config.owner_name;

            // Update floating button links
            const floatWhatsappBtn = document.getElementById('floatWhatsappBtn');
            if (floatWhatsappBtn) floatWhatsappBtn.href = `https://wa.me/${config.whatsapp_num}?text=Hi%20HI-TECH%20AIRCONS%2C%20I%20would%20like%20to%20book%20a%20service%20for%20my%20AC.`;

            const heroWhatsappBtn = document.getElementById('heroWhatsappBtn');
            if (heroWhatsappBtn) heroWhatsappBtn.href = `https://wa.me/${config.whatsapp_num}?text=Hi%20HI-TECH%20AIRCONS%2C%20I%20would%20like%20to%20enquire%20about%20AC%20sales/service.`;

            const floatCallBtn = document.getElementById('floatCallBtn');
            if (floatCallBtn) floatCallBtn.href = `tel:${config.phone1.replace(/\s+/g, '')}`;

            const heroCallBtn = document.getElementById('heroCallBtn');
            if (heroCallBtn) heroCallBtn.href = `tel:${config.phone1.replace(/\s+/g, '')}`;

            // Cache bust local assets on page load to display updated configurations
            const timestamp = Date.now();
            document.querySelectorAll('img').forEach(img => {
                const src = img.getAttribute('src');
                if (src && src.startsWith('assets/')) {
                    img.src = `${src.split('?')[0]}?t=${timestamp}`;
                }
            });

        } catch (err) {
            console.error("Error loading site config:", err);
        }
    }
    loadWebsiteConfig();

    // 1. STICKY HEADER SCROLL WORKFLOW
    const header = document.getElementById('mainHeader');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });

    // 2. MOBILE HAMBURGER AND DRAWER MENU
    const menuToggle = document.getElementById('menuToggle');
    const mobileDrawer = document.getElementById('mobileDrawer');
    const mobileOverlay = document.getElementById('mobileOverlay');
    const mobileLinks = mobileDrawer.querySelectorAll('.nav-link');

    function toggleMobileMenu() {
        const isOpen = mobileDrawer.classList.contains('open');
        if (isOpen) {
            mobileDrawer.classList.remove('open');
            mobileOverlay.classList.remove('open');
            document.body.style.overflow = '';
        } else {
            mobileDrawer.classList.add('open');
            mobileOverlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
    }

    menuToggle.addEventListener('click', toggleMobileMenu);
    mobileOverlay.addEventListener('click', toggleMobileMenu);
    
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (mobileDrawer.classList.contains('open')) {
                toggleMobileMenu();
            }
        });
    });

    // 3. SERVICE BOOKING MODAL (INTEGRATED WITH SQL DATABASE)
    const bookingModal = document.getElementById('bookingModal');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const bookingForm = document.getElementById('bookingForm');
    const bookTriggers = document.querySelectorAll('.btn-book-trigger');

    function openBookingModal(e) {
        if (e) e.preventDefault();
        bookingModal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeBookingModal() {
        bookingModal.classList.remove('open');
        if (!mobileDrawer.classList.contains('open') && !brandModal.classList.contains('open')) {
            document.body.style.overflow = '';
        }
    }

    bookTriggers.forEach(trigger => {
        trigger.addEventListener('click', openBookingModal);
    });

    modalCloseBtn.addEventListener('click', closeBookingModal);
    
    bookingModal.addEventListener('click', (e) => {
        if (e.target === bookingModal) {
            closeBookingModal();
        }
    });

    // Success Modal References & Helpers
    const successModal = document.getElementById('successModal');
    const successCloseBtn = document.getElementById('successCloseBtn');
    const btnSuccessOk = document.getElementById('btnSuccessOk');
    const successModalMsg = document.getElementById('successModalMsg');

    function openSuccessModal(message) {
        successModalMsg.innerText = message;
        successModal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeSuccessModal() {
        successModal.classList.remove('open');
        if (!mobileDrawer.classList.contains('open') && !bookingModal.classList.contains('open') && !brandModal.classList.contains('open')) {
            document.body.style.overflow = '';
        }
    }

    if (successCloseBtn) successCloseBtn.addEventListener('click', closeSuccessModal);
    if (btnSuccessOk) btnSuccessOk.addEventListener('click', closeSuccessModal);
    if (successModal) {
        successModal.addEventListener('click', (e) => {
            if (e.target === successModal) {
                closeSuccessModal();
            }
        });
    }

    // SUBMIT DATA TO SQLite VIA FLASK API
    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('bookingName').value.trim();
        const phone = document.getElementById('bookingPhone').value.trim();
        const service = document.getElementById('bookingService').value;
        const notes = document.getElementById('bookingNotes').value.trim();
        const btnSubmit = document.getElementById('btnSubmitBooking');
        
        // Show loading state
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving Request...';

        try {
            const response = await fetch('/api/book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, phone, service, notes })
            });

            const result = await response.json();
            
            if (result.success) {
                // Close booking modal
                closeBookingModal();
                // Show Custom Premium Success Dialog
                openSuccessModal("Your service request has been successfully processed and priority scheduling is granted. A dedicated cooling coordinator will contact you shortly.");
                bookingForm.reset();
            } else {
                alert(`Error: ${result.error || "Failed to submit request."}`);
            }
        } catch (err) {
            alert("Network error occurred. The server might be offline. Request was not saved.");
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Submit Service Request';
        }
    });

    // 4. INTERACTIVE BRANDS SHOWCASE MODAL WITH REAL AC PRODUCTS
    const brandModal = document.getElementById('brandModal');
            const brandModalCloseBtn = document.getElementById('brandModalCloseBtn');
            const brandModalTitle = document.getElementById('brandModalTitle');
            const brandProductsGrid = document.getElementById('brandProductsGrid');
            const brandCards = document.querySelectorAll('.brand-card');

            // Fetch and cache brand products configuration
            let brandACData = {};
            async function loadBrandProductsConfig() {
                try {
                    const response = await fetch('/api/products');
                    if (response.ok) {
                        brandACData = await response.json();
                    }
                } catch (err) {
                    console.error("Error loading brand products config:", err);
                }
            }
            loadBrandProductsConfig();

    function openBrandModal(brandKey) {
        const data = brandACData[brandKey];
        if (!data) return;

        brandModalTitle.innerText = data.title;
        document.getElementById('brandModalSub').innerText = data.sub;
        
        brandProductsGrid.innerHTML = '';
        
        data.products.forEach(p => {
            const card = document.createElement('div');
            card.className = 'product-card';
            card.innerHTML = `
                <img src="${p.image}" alt="${p.name}" class="product-image">
                <h4 class="product-title">${p.name}</h4>
                <p class="product-specs">${p.specs}</p>
                <div class="product-footer">
                    <span class="product-price">${p.price}</span>
                    <button class="btn-product-book" onclick="bookProduct('${data.title}', '${p.name}')">Enquire Now</button>
                </div>
            `;
            brandProductsGrid.appendChild(card);
        });

        brandModal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    function closeBrandModal() {
        brandModal.classList.remove('open');
        if (!mobileDrawer.classList.contains('open') && !bookingModal.classList.contains('open')) {
            document.body.style.overflow = '';
        }
    }

    brandCards.forEach(card => {
        card.addEventListener('click', () => {
            const brandKey = card.getAttribute('data-brand-color');
            openBrandModal(brandKey);
        });
        card.style.cursor = 'pointer'; // Visual feedback on desktop
    });

    brandModalCloseBtn.addEventListener('click', closeBrandModal);
    
    brandModal.addEventListener('click', (e) => {
        if (e.target === brandModal) {
            closeBrandModal();
        }
    });

    // Global helper so child buttons inside modal can launch form
    window.bookProduct = function(brand, model) {
        closeBrandModal();
        
        // Populate booking notes
        document.getElementById('bookingNotes').value = `Hi, I am interested in purchasing/enquiring about: ${brand} - ${model}.`;
        // Pre-select Sales dropdown option
        document.getElementById('bookingService').value = 'sales';
        
        // Open the booking modal
        openBookingModal();
    };


    // 5. ACTIVE NAVIGATION LINK ON SCROLL
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.desktop-nav .nav-link, .mobile-nav .nav-link');

    window.addEventListener('scroll', () => {
        let currentSection = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.scrollY >= (sectionTop - sectionHeight * 0.4)) {
                currentSection = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${currentSection}`) {
                link.classList.add('active');
            }
        });
    });

    // 6. GALLERY CATEGORY FILTERS
    const filterButtons = document.querySelectorAll('.gallery-filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filterValue = btn.getAttribute('data-filter');
            
            galleryItems.forEach(item => {
                if (filterValue === 'all' || item.getAttribute('data-category') === filterValue) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'scale(1)';
                    }, 50);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });

    // 7. CUSTOM TESTIMONIALS SLIDER
    const track = document.getElementById('testimonialTrack');
    const slides = Array.from(track.children);
    const dotsContainer = document.getElementById('sliderDots');
    let currentIndex = 0;
    let autoPlayInterval;

    slides.forEach((slide, idx) => {
        const dot = document.createElement('div');
        dot.className = 'dot';
        if (idx === 0) dot.classList.add('active');
        dot.addEventListener('click', () => {
            goToSlide(idx);
            resetAutoPlay();
        });
        dotsContainer.appendChild(dot);
    });

    const dots = Array.from(dotsContainer.children);

    function goToSlide(index) {
        track.style.transform = `translateX(-${index * 100}%)`;
        dots[currentIndex].classList.remove('active');
        dots[index].classList.add('active');
        currentIndex = index;
    }

    function nextSlide() {
        let nextIndex = currentIndex + 1;
        if (nextIndex >= slides.length) {
            nextIndex = 0;
        }
        goToSlide(nextIndex);
    }

    function startAutoPlay() {
        autoPlayInterval = setInterval(nextSlide, 5000);
    }

    function resetAutoPlay() {
        clearInterval(autoPlayInterval);
        startAutoPlay();
    }

    startAutoPlay();

    // Arrow navigation listeners
    const prevBtn = document.getElementById('sliderPrevBtn');
    const nextBtn = document.getElementById('sliderNextBtn');

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            let prevIndex = currentIndex - 1;
            if (prevIndex < 0) {
                prevIndex = slides.length - 1;
            }
            goToSlide(prevIndex);
            resetAutoPlay();
        });

        nextBtn.addEventListener('click', () => {
            nextSlide();
            resetAutoPlay();
        });
    }

    let startX = 0;
    let isDragging = false;

    track.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        isDragging = true;
    });

    track.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        const currentX = e.touches[0].clientX;
        const diffX = startX - currentX;
        
        if (Math.abs(diffX) > 60) {
            if (diffX > 0) {
                nextSlide();
            } else {
                let prevIndex = currentIndex - 1;
                if (prevIndex < 0) prevIndex = slides.length - 1;
                goToSlide(prevIndex);
            }
            isDragging = false;
            resetAutoPlay();
        }
    });

    track.addEventListener('touchend', () => {
        isDragging = false;
    });

    // 8. SCROLL-REVEAL OBSERVER
    const revealElements = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.15
    });

    revealElements.forEach(el => {
        revealObserver.observe(el);
    });
});
