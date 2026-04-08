const CACHE_NAME = 'happy-kids-v1';
const urlsToCache = ['/', '/index.html'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(urlsToCache)));
});

self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});    <script>
        // ===== NAVIGATION =====
        function goTo(section, el) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('section-'+section).classList.add('active');
            el.classList.add('active');
            if(section==='inicio') loadReels();
            if(section==='colorear') loadCatalog();
            if(section==='mate') initMath();
        }

        function showToast(msg) {
            const t=document.getElementById('toast');
            t.textContent=msg; t.classList.add('show');
            setTimeout(()=>t.classList.remove('show'),3000);
        }

        // ===== CLOUDINARY CONFIG =====
        const CLOUD_NAME = 'dgdw8fbku';
        
        function getVideoUrl(publicId) {
            return `https://res.cloudinary.com/${CLOUD_NAME}/video/upload/q_auto,f_mp4/${publicId}`;
        }
        
        function getImageUrl(publicId) {
            return `https://res.cloudinary.com/${CLOUD_NAME}/image/upload/q_auto/${publicId}`;
        }

        // ===== PRODUCT DATA (15 items) =====
        const products = [
            {id:'galaxy-watch',name:'Galaxy Watch Ultra',cat:'fisico',badge:'⌚ Nuevo',orig:12999,final:8999,video:'Samsung_Galaxy_Watch_Ultra_rbrkd0',url:'https://meli.la/1gMTZhz',views:'18.5k'},
            {id:'nautica',name:'Nautica Voyage',cat:'fisico',badge:'🌊 Top',orig:599,final:299,video:'Nautica_voyage_eau_de_toilette_trending_unboxing_bestmensfragrance_parfumrecommended_fragrance_rALDtQpyUXU_l1zz6m',url:'https://meli.la/2wumBgh',views:'22.3k'},
            {id:'s25',name:'Samsung S25 FE',cat:'fisico',badge:'🔥 Flash',orig:13999,final:8999,video:'Samsung_Galaxy_S25_FE_ggualp',url:'https://meli.la/2mA4qCh',views:'12.4k'},
            {id:'moto',name:'Moto Edge 50 Pro',cat:'fisico',badge:'💎 Premium',orig:12999,final:7999,video:'Motorola_Edición_Premium_nouj95',url:'https://meli.la/23KvNjV',views:'8.7k'},
            {id:'pistola',name:'Pistola Masaje Xiaomi',cat:'fisico',badge:'💆 #1',orig:899,final:299,video:'Pistola_masaje_Xiaomi_me_encanta_️_Ij6vVKFiEKY_oz5c9x',url:'https://meli.la/1FfMYZi',views:'35.6k'},
            {id:'curren',name:'Curren 8402 Luxury',cat:'fisico',badge:'⌚ Lujo',orig:1299,final:599,video:'reloj_curren_8402_tzmw3l',url:'https://meli.la/1wiPMys',views:'24.1k'},
            {id:'espejo',name:'Espejo LED Táctil',cat:'fisico',badge:'✨ LED',orig:899,final:550,video:'espejo2_nwhn93',url:'https://meli.la/1kYoTt1',views:'4.7k'},
            {id:'camara',name:'Cámara WiFi 360°',cat:'fisico',badge:'🏠 Seguridad',orig:1599,final:899,video:'camara_de_seguridad_2_uk1o5b',url:'https://meli.la/29JngVu',views:'6.3k'},
            {id:'taladro',name:'Taladro Miwod 21V',cat:'fisico',badge:'🔧 Best',orig:1299,final:599,video:'taladro1_yyp5nz',url:'https://meli.la/1XwiFN1',views:'31.8k'},
            {id:'carpa',name:'Carpa Styrka 3x3',cat:'fisico',badge:'⛺ Outdoor',orig:1950,final:799,video:'Toldo_Plegable_3x3_Aleman_-_Vanlig_-_Exterior_IQZVxYT0IBg_1_hldbyk',url:'https://meli.la/31DDvzp',views:'15.2k'},
            {id:'naranja',name:'Producto Naranja',cat:'fisico',badge:'🍊 Nuevo',orig:2999,final:2036,video:'3_naranja_ddfajm',url:'https://meli.la/1eMktrC',views:'5.8k'},
            {id:'cargador',name:'Cargador GaN 20W',cat:'fisico',badge:'⚡ #1',orig:98,final:69,img:true,images:['D_Q_NP_880828-MLA100062693161_122025-O.webp','D_Q_NP_919962-MLA83906488340_042025-O.webp'],url:'https://meli.la/1WTtdAw',views:'45.2k'},
            {id:'leon',name:'El León Valiente',cat:'digital',badge:'📚 FREE',orig:0,final:0,video:'Cuento_1_El_Leon_Happy_jujtwm',pdf:'https://drive.google.com/file/d/1HrFakhKIwAXAYs7zNZMFpDrx7h2YSCqT/view',views:'45.2k'},
            {id:'animalitos',name:'Animalitos Divertidos',cat:'digital',badge:'📚 FREE',orig:0,final:0,video:'animalitos_dwothk',pdf:'https://drive.google.com/file/d/1qCV6KI6eU3E3zD_sH_dXNPkQV3EzIo6f/view',views:'38.7k'},
            {id:'emociones',name:'Mis Emociones',cat:'digital',badge:'📚 FREE',orig:0,final:0,video:'emociones_rwg9cf',pdf:'https://drive.google.com/file/d/1RNbc5sOcslreFlxeWgBABLdQ4fxoK_7F/view',views:'52.1k'},
            {id:'familia',name:'Mi Familia',cat:'digital',badge:'📚 FREE',orig:0,final:0,video:'familia_ed04bv',pdf:'https://drive.google.com/file/d/1CNieuZWxl8sHcVuk6TiGd2rH0pkf5GeC/view',views:'41.3k'}
        ];

        // ===== REELS LOADER =====
        let currentReel = 0;
        let reelsObserver;

        function loadReels() {
            const container = document.getElementById('reelsContainer');
            if(container.children.length > 0) return; // Ya cargado
            
            products.forEach((p, idx) => {
                const reel = document.createElement('div');
                reel.className = 'reel-card';
                reel.dataset.index = idx;
                
                const isDigital = p.cat === 'digital';
                const discount = p.orig > 0 ? Math.round((1 - p.final/p.orig)*100) : 0;
                
                let mediaHtml;
                if(p.img) {
                    // Carrusel de imágenes para cargador
                    mediaHtml = `
                        <div class="carousel-container" id="carousel-${p.id}">
                            ${p.images.map((img,i) => `
                                <div class="carousel-slide ${i===0?'active':''}">
                                    <img src="https://http2.mlstatic.com/${img}" alt="${p.name}" loading="lazy">
                                </div>
                            `).join('')}
                            <button class="carousel-prev" onclick="changeSlide(-1,'${p.id}')">❮</button>
                            <button class="carousel-next" onclick="changeSlide(1,'${p.id}')">❯</button>
                            <div class="carousel-dots">
                                ${p.images.map((_,i) => `<span class="dot ${i===0?'active':''}" onclick="goSlide(${i},'${p.id}')"></span>`).join('')}
                            </div>
                        </div>
                    `;
                } else {
                    mediaHtml = `
                        <video class="reel-video" loop playsinline muted preload="metadata" 
                               poster="${getImageUrl(p.video+'.jpg')}">
                            <source src="${getVideoUrl(p.video)}" type="video/mp4">
                        </video>
                    `;
                }
                
                reel.innerHTML = `
                    ${mediaHtml}
                    <div class="reel-overlay"></div>
                    <div class="reel-content">
                        <span class="reel-badge">${p.badge}</span>
                        <h2 class="reel-title">${p.name}</h2>
                        <div class="reel-price-box">
                            ${p.orig > 0 ? `<span class="reel-original">$${p.orig} MXN</span>` : ''}
                            <span class="reel-final">${p.final > 0 ? '$'+p.final+' MXN' : 'GRATIS'}</span>
                            ${discount > 0 ? `<span class="reel-discount">⬇️ ${discount}%</span>` : ''}
                        </div>
                        <div class="reel-actions">
                            ${isDigital ? 
                                `<button class="btn-reel btn-reel-primary" onclick="downloadPDF('${p.pdf}')">📥 Descargar</button>` :
                                `<a href="${p.url}" class="btn-reel btn-reel-primary" target="_blank" onclick="trackClick('${p.id}')">🛒 Comprar</a>`
                            }
                            <button class="btn-reel btn-reel-secondary" onclick="shareProduct('${p.name}','${p.final}')">📤</button>
                        </div>
                    </div>
                    <div class="reel-side-actions">
                        <button class="side-btn" onclick="toggleLike(this)">❤️</button>
                        <button class="side-btn" onclick="shareProduct('${p.name}','${p.final}')">📤</button>
                        <div style="text-align:center;font-size:12px;color:white;margin-top:4px">${p.views}</div>
                    </div>
                `;
                
                container.appendChild(reel);
            });
            
            setupVideoObserver();
        }

        // ===== VIDEO AUTO-PLAY OBSERVER =====
        function setupVideoObserver() {
            const videos = document.querySelectorAll('.reel-video');
            
            reelsObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    const video = entry.target;
                    if(entry.isIntersecting && entry.intersectionRatio > 0.6) {
                        video.play().catch(e => console.log('Autoplay prevented'));
                        currentReel = parseInt(video.closest('.reel-card').dataset.index);
                    } else {
                        video.pause();
                        video.currentTime = 0;
                    }
                });
            }, { threshold: [0.6] });
            
            videos.forEach(v => reelsObserver.observe(v));
        }

        // ===== CATALOG GRID =====
        function loadCatalog() {
            const grid = document.getElementById('catalogGrid');
            if(grid.children.length > 0) return;
            
            products.filter(p => p.cat === 'fisico').forEach(p => {
                const discount = Math.round((1 - p.final/p.orig)*100);
                const card = document.createElement('div');
                card.className = 'product-card';
                card.innerHTML = `
                    <img src="${p.img ? 'https://http2.mlstatic.com/'+p.images[0] : getImageUrl(p.video+'.jpg')}" 
                         class="product-image" alt="${p.name}" loading="lazy">
                    <div class="product-info">
                        <div class="product-name">${p.name}</div>
                        <div class="product-price-row">
                            <span class="product-original">$${p.orig}</span>
                            <span class="product-final">$${p.final}</span>
                            <span class="product-discount">-${discount}%</span>
                        </div>
                        <a href="${p.url}" class="btn-buy-mini" target="_blank" onclick="trackClick('${p.id}')">Ver en Mercado Libre</a>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        // ===== CAROUSEL LOGIC =====
        let carousels = {};
        
        function changeSlide(dir, id) {
            const c = carousels[id] || { current: 0, total: 3 };
            c.current = (c.current + dir + c.total) % c.total;
            carousels[id] = c;
            updateCarousel(id, c.current);
        }
        
        function goSlide(idx, id) {
            carousels[id] = { ...(carousels[id] || {total:3}), current: idx };
            updateCarousel(id, idx);
        }
        
        function updateCarousel(id, current) {
            const container = document.getElementById('carousel-'+id);
            if(!container) return;
            container.querySelectorAll('.carousel-slide').forEach((s,i) => {
                s.classList.toggle('active', i === current);
            });
            container.querySelectorAll('.dot').forEach((d,i) => {
                d.classList.toggle('active', i === current);
            });
        }

        // ===== UTILITIES =====
        function toggleLike(btn) {
            btn.style.transform = btn.style.transform === 'scale(1.2)' ? '' : 'scale(1.2)';
            btn.style.filter = btn.style.filter ? '' : 'drop-shadow(0 0 10px #ff6b6b)';
        }

        function shareProduct(name, price) {
            const text = price > 0 ? 
                `🔥 ${name} por solo $${price} MXN en Happy Kids!` : 
                `📚 ${name} GRATIS en Happy Kids!`;
            
            if(navigator.share) {
                navigator.share({ title: 'Happy Kids', text: text, url: window.location.href });
            } else {
                navigator.clipboard.writeText(text + ' ' + window.location.href);
                showToast('¡Link copiado!');
            }
        }

        function downloadPDF(url) {
            window.open(url, '_blank');
            showToast('📥 Abriendo PDF...');
        }

        function trackClick(id) {
            console.log('Click tracked:', id);
            // Aquí puedes agregar analytics
        }

        // ===== INITIAL LOAD =====
        window.addEventListener('DOMContentLoaded', () => {
            loadReels();
        });
    </script>
