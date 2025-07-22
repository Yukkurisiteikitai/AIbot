
        // サンプルデータ
        const graphData = {
            nodes: [
                {
                    "id": 1001,
                    "title": "幼少期に何があったか",
                    "context": "幼少期に、周囲に家がある田舎と都会の中間くらいの都市で育った。小学4年生の時にTokyo Game Showに行ったことがきっかけで、ゲーム制作に興味を持ち、3ヶ月かけてクソゲーを作った。",
                    "links": [
                    { "id": 1006, "weight": 0.9 },
                    { "id": 1019, "weight": 0.8 }
                    ]
                },
                {
                    "id": 1002,
                    "title": "周囲の人の様子",
                    "context": "小学校の先生の影響を強く受け、作れば自分の欲を叶えられるという考え方を学んだ。周囲からは「聞き魔」と呼ばれる。",
                    "links": [
                    { "id": 1006, "weight": 0.7 },
                    { "id": 1017, "weight": 0.9 }
                    ]
                },
                {
                    "id": 1003,
                    "title": "コンプレックス等の自分のあまり伝えなかった点",
                    "context": "強迫観念があり、謎の天使と悪魔のような存在が頭の中に現れる。社会的にまずいと思われる可能性があるため、他人にはあまり話さない。",
                    "links": [
                    { "id": 1011, "weight": 0.6 },
                    { "id": 1018, "weight": 0.5 }
                    ]
                },
                {
                    "id": 1004,
                    "title": "性格の特徴",
                    "context": "今を全力で生きることを重視し、真面目で集中力がある。一方で視野が狭く、不注意な面もある。周囲からは真面目な性格で、哲学が好きな変わり者だと言われる。",
                    "links": [
                    { "id": 1005, "weight": 0.8 },
                    { "id": 1013, "weight": 0.6 },
                    { "id": 1017, "weight": 0.7 },
                    { "id": 1020, "weight": 0.9 }
                    ]
                },
                {
                    "id": 1005,
                    "title": "信念・価値観",
                    "context": "裏切らないことを最も大切にし、自分が決めたルールは破らない。毎日を全力でやることはやったと言える生き方が理想。",
                    "links": [
                    { "id": 1004, "weight": 0.8 },
                    { "id": 1007, "weight": 0.5 },
                    { "id": 1013, "weight": 0.7 },
                    { "id": 1020, "weight": 0.9 }
                    ]
                },
                {
                    "id": 1006,
                    "title": "趣味・興味",
                    "context": "人がどんな考えを持っているのかに興味がある。趣味はゲーム作りで、自分の欲を叶えるために自由に設定を盛り込んだゲームを制作し、販売している。",
                    "links": [
                    { "id": 1001, "weight": 0.9 },
                    { "id": 1002, "weight": 0.7 },
                    { "id": 1009, "weight": 0.6 }
                    ]
                },
                {
                    "id": 1007,
                    "title": "対人関係のスタイル",
                    "context": "初対面の人とは、相手が嫌がらないように心がけて接する。親しい友人とは本音で言い合える関係を築いている。人との距離感は慎重に調節していくべきだと考えている。",
                    "links": [
                    { "id": 1005, "weight": 0.5 },
                    { "id": 1018, "weight": 0.7 },
                    { "id": 1019, "weight": 0.4 }
                    ]
                },
                {
                    "id": 1008,
                    "title": "感情の反応",
                    "context": "問題を解決した時や、作ったもので人が幸せになった時に喜びを感じる。大切にしている人や物が自分のせいで被害を被った時に悲しみを感じ、大切にしていたものが壊された時に怒りを感じる。同じ問題に対して進捗があまり感じられない時にストレスを感じやすい。",
                    "links": [
                    { "id": 1012, "weight": 0.9 },
                    { "id": 1013, "weight": 0.6 },
                    { "id": 1014, "weight": 0.5 }
                    ]
                },
                {
                    "id": 1009,
                    "title": "理想・夢",
                    "context": "将来はどんな課題でもより良くカスタマイズしたものを提出できるようにしたい。自分が作ったもので自分がより楽に暮らせるような人生を送りたい。今後の世代が少しでも続いてくれるような社会を実現したい。",
                    "links": [
                    { "id": 1006, "weight": 0.6 },
                    { "id": 1011, "weight": 0.5 },
                    { "id": 1020, "weight": 0.7 }
                    ]
                },
                {
                    "id": 1010,
                    "title": "過去の失敗と学び",
                    "context": "コンテストに応募しようとしたが期限切れで応募できなかった。この経験から、早い段階で行動すること、だらだらしないこと、現実を直視することの重要性を学んだ。",
                    "links": [
                    { "id": 1011, "weight": 0.4 },
                    { "id": 1014, "weight": 0.6 }
                    ]
                },
                {
                    "id": 1011,
                    "title": "内面の葛藤",
                    "context": "現実と理想の間で葛藤している。やりたいことがたくさんあるが、今やっていることを修了するまではそれをすることが許されないため、優先順位をつけざるを得ない状況。",
                    "links": [
                    { "id": 1003, "weight": 0.6 },
                    { "id": 1009, "weight": 0.5 },
                    { "id": 1010, "weight": 0.4 },
                    { "id": 1016, "weight": 0.8 }
                    ]
                },
                {
                    "id": 1012,
                    "title": "感情のトリガー",
                    "context": "自分が考えたことが叶った時に嬉しさを感じ、他者や自分の大切なものに危害が加えられた時に悲しみや怒りを感じる。自分がやらなければいけないことをしていない時に不安を感じる。",
                    "links": [
                    { "id": 1008, "weight": 0.9 },
                    { "id": 1005, "weight": 0.6 }
                    ]
                },
                {
                    "id": 1013,
                    "title": "行動のパターン",
                    "context": "ストレスを感じた時にやるべきことに力を入れる。自分が決めたことは得意で、素直にミスを認めやすい。無意識のうちに何が問題かを考えている。",
                    "links": [
                    { "id": 1004, "weight": 0.6 },
                    { "id": 1005, "weight": 0.7 },
                    { "id": 1008, "weight": 0.6 },
                    { "id": 1014, "weight": 0.7 }
                    ]
                },
                {
                    "id": 1014,
                    "title": "思考プロセス",
                    "context": "何かを決断する時は、現状が良くなるかを考える。問題を解決する時は、観察->検証 -> 解決策 -> 解決という手順を踏む。新しいことを学ぶ時は、まず何のための学びかを観察し、具体例を学んでから概念として捉える。",
                    "links": [
                    { "id": 1008, "weight": 0.5 },
                    { "id": 1013, "weight": 0.7 }
                    ]
                },
                {
                    "id": 1015,
                    "title": "言動の癖",
                    "context": "「私は」という言葉をよく使う。頷いたり肯定するジェスチャーをするが、心の中ではただの情報としてカウントしていることが多い。",
                    "links": [
                    { "id": 1017, "weight": 0.4 }
                    ]
                },
                {
                    "id": 1016,
                    "title": "価値観の変遷",
                    "context": "根本的な価値観はあまり変わっていないが、叶えられるものは限り少ないので優先順位をしっかり考えるようになった。",
                    "links": [
                    { "id": 1011, "weight": 0.8 },
                    { "id": 1005, "weight": 0.4 }
                    ]
                },
                {
                    "id": 1017,
                    "title": "自己認識",
                    "context": "人に聞きまくる人間の考えを知るのが好きな生命体だと考えている。長所は集中する時間が長いことで、短所は不注意であること。他人からは人に聞きまくる人だと思われている。",
                    "links": [
                    { "id": 1002, "weight": 0.9 },
                    { "id": 1004, "weight": 0.7 },
                    { "id": 1006, "weight": 0.5 }
                    ]
                },
                {
                    "id": 1018,
                    "title": "対立と解決の方法",
                    "context": "他人と意見が対立した場合は、できるだけ納得がいくようにするが、考え方が違うなら離れる。人間関係でトラブルが起きた場合は、責任のありどころを明示して解決しようとするが、ダメなら逃げる。対立やトラブルを避けるために、自分の考えをあまり明確に定義しないようにしている。",
                    "links": [
                    { "id": 1003, "weight": 0.5 },
                    { "id": 1007, "weight": 0.7 }
                    ]
                },
                {
                    "id": 1019,
                    "title": "対人関係の歴史",
                    "context": "人間に対して好きだと言ったことを否定されたことが印象に残っている。Tokyo Game Showでゲーム制作者からフィードバックを受けられたことが成功体験。我を知らない人に見せて引かれた時に小出しにすることのリスクを学んだ。",
                    "links": [
                    { "id": 1001, "weight": 0.8 },
                    { "id": 1007, "weight": 0.4 }
                    ]
                },
                {
                    "id": 1020,
                    "title": "将来への不安と希望",
                    "context": "将来に対する不安はあまりない。自分が良くなった素敵な未来があるだろうと考えている。どこで死んでも良い、今を全力に生きれるような人でありたいと考えている。",
                    "links": [
                    { "id": 1004, "weight": 0.9 },
                    { "id": 1005, "weight": 0.9 },
                    { "id": 1009, "weight": 0.7 }
                    ]
                }
            ]
        };

        class DynamicGraph {
            constructor() {
                this.container = document.getElementById('graphContainer');
                this.minimap = document.getElementById('minimap');
                this.nodes = new Map();
                this.connections = new Map();
                this.particles = [];
                this.animationActive = false;
                this.currentScale = 1;
                this.currentOffsetX = 0;
                this.currentOffsetY = 0;
                
                // パン操作用の変数
                this.isDragging = false;
                this.lastMouseX = 0;
                this.lastMouseY = 0;
                this.keys = {};
                
                // ミニマップ用の変数
                this.worldBounds = { minX: 0, minY: 0, maxX: 0, maxY: 0 };
                
                this.init();
            }

            init() {
                this.createNodes();
                this.createConnections();
                this.setupSearch();
                this.setupControls();
                this.setupMinimap();
                this.startRenderLoop();
            }

            createNodes() {
                const containerWidth = window.innerWidth;
                const containerHeight = window.innerHeight;

                graphData.nodes.forEach((nodeData, index) => {
                    const node = document.createElement('div');
                    node.className = 'node';
                    node.id = `node-${nodeData.id}`;
                    
                    // タイトルを30文字以内に制限
                    const title = nodeData.title.length > 30 ? 
                        nodeData.title.substring(0, 27) + '...' : nodeData.title;
                    node.textContent = title;

                    // 円形配置の計算
                    const angle = (index / graphData.nodes.length) * 2 * Math.PI;
                    const radius = Math.min(containerWidth, containerHeight) * 0.3;
                    const centerX = containerWidth / 2;
                    const centerY = containerHeight / 2;
                    
                    const x = centerX + radius * Math.cos(angle);
                    const y = centerY + radius * Math.sin(angle);

                    const size = 60 + Math.random() * 40;
                    node.style.width = size + 'px';
                    node.style.height = size + 'px';
                    node.style.left = (x - size/2) + 'px';
                    node.style.top = (y - size/2) + 'px';
                    node.style.fontSize = (12 + Math.random() * 4) + 'px';

                    node.addEventListener('click', () => this.selectNode(nodeData));
                    
                    this.container.appendChild(node);
                    this.nodes.set(nodeData.id, {
                        element: node,
                        data: nodeData,
                        x: x,
                        y: y,
                        size: size
                    });
                });

                // 世界の境界を計算
                this.calculateWorldBounds();
            }

            createConnections() {
                graphData.nodes.forEach(nodeData => {
                    nodeData.links.forEach(linkId => {
                        const fromNode = this.nodes.get(nodeData.id);
                        const toNode = this.nodes.get(linkId);
                        
                        if (fromNode && toNode && nodeData.id < linkId) { // 重複を避ける
                            this.createConnection(fromNode, toNode);
                        }
                    });
                });
            }

            createConnection(fromNode, toNode) {
                const connection = document.createElement('div');
                connection.className = 'connection';
                
                const dx = toNode.x - fromNode.x;
                const dy = toNode.y - fromNode.y;
                const length = Math.sqrt(dx * dx + dy * dy);
                const angle = Math.atan2(dy, dx);
                
                connection.style.width = length + 'px';
                connection.style.left = fromNode.x + 'px';
                connection.style.top = fromNode.y + 'px';
                connection.style.transform = `rotate(${angle}rad)`;
                
                this.container.appendChild(connection);
                
                const connectionKey = `${fromNode.data.id}-${toNode.data.id}`;
                this.connections.set(connectionKey, {
                    element: connection,
                    from: fromNode,
                    to: toNode,
                    length: length,
                    angle: angle
                });
            }

            setupSearch() {
                const searchInput = document.getElementById('searchInput');
                const searchResults = document.getElementById('searchResults');

                searchInput.addEventListener('input', (e) => {
                    const query = e.target.value.toLowerCase();
                    this.clearHighlights();
                    
                    if (query.length < 2) {
                        searchResults.innerHTML = '';
                        return;
                    }

                    const matches = graphData.nodes.filter(node => 
                        node.title.toLowerCase().includes(query) ||
                        node.context.toLowerCase().includes(query)
                    );

                    searchResults.innerHTML = matches.map(node => 
                        `<div class="result-item" data-node-id="${node.id}">
                            <strong>${node.title}</strong>
                            <button class="flow-btn" onclick="graph.focusOnNode(${node.id})">流れを見る</button>
                            <br><small>${node.context.substring(0, 50)}...</small>
                        </div>`
                    ).join('');

                    // 検索結果をクリックで選択
                    searchResults.querySelectorAll('.result-item').forEach(item => {
                        item.addEventListener('click', (e) => {
                            if (e.target.classList.contains('flow-btn')) return;
                            const nodeId = parseInt(item.dataset.nodeId);
                            this.selectNode(graphData.nodes.find(n => n.id === nodeId));
                        });
                    });
                });
            }

            selectNode(nodeData) {
                this.clearHighlights();
                
                const nodeElement = this.nodes.get(nodeData.id);
                nodeElement.element.classList.add('highlighted');
                
                this.showNodeInfo(nodeData);
                this.highlightConnections(nodeData.id);
            }

            focusOnNode(nodeId) {
                const node = this.nodes.get(nodeId);
                if (!node) return;

                this.selectNode(node.data);
                
                // カメラを該当ノードにズーム
                const targetX = window.innerWidth / 2 - node.x;
                const targetY = window.innerHeight / 2 - node.y;
                
                this.animateCamera(targetX, targetY, 1.5);
                this.startFlowAnimation(nodeId);
            }

            animateCamera(targetX, targetY, targetScale) {
                const duration = 1000;
                const startTime = Date.now();
                const startX = this.currentOffsetX;
                const startY = this.currentOffsetY;
                const startScale = this.currentScale;
                
                const animate = () => {
                    const elapsed = Date.now() - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const eased = this.easeInOutCubic(progress);
                    
                    this.currentOffsetX = startX + (targetX - startX) * eased;
                    this.currentOffsetY = startY + (targetY - startY) * eased;
                    this.currentScale = startScale + (targetScale - startScale) * eased;
                    
                    this.applyTransform();
                    
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    }
                };
                
                animate();
            }

            applyTransform() {
                this.container.style.transform = 
                    `translate(${this.currentOffsetX}px, ${this.currentOffsetY}px) scale(${this.currentScale})`;
            }

            easeInOutCubic(t) {
                return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
            }

            startFlowAnimation(nodeId) {
                this.animationActive = true;
                const node = this.nodes.get(nodeId);
                
                node.data.links.forEach(linkId => {
                    const connectionKey = nodeId < linkId ? `${nodeId}-${linkId}` : `${linkId}-${nodeId}`;
                    const connection = this.connections.get(connectionKey);
                    
                    if (connection) {
                        connection.element.classList.add('active');
                        this.createFlowParticles(connection);
                    }
                });
            }

            createFlowParticles(connection) {
                const particleCount = 3;
                
                for (let i = 0; i < particleCount; i++) {
                    setTimeout(() => {
                        if (!this.animationActive) return;
                        
                        const particle = document.createElement('div');
                        particle.className = 'particle';
                        this.container.appendChild(particle);
                        
                        this.animateParticle(particle, connection);
                    }, i * 500);
                }
            }

            animateParticle(particle, connection) {
                const duration = 2000;
                const startTime = Date.now();
                
                const animate = () => {
                    if (!this.animationActive) {
                        particle.remove();
                        return;
                    }
                    
                    const elapsed = Date.now() - startTime;
                    const progress = (elapsed / duration) % 1;
                    
                    const x = connection.from.x + (connection.to.x - connection.from.x) * progress;
                    const y = connection.from.y + (connection.to.y - connection.from.y) * progress;
                    
                    particle.style.left = (x - 3) + 'px';
                    particle.style.top = (y - 3) + 'px';
                    
                    if (elapsed < duration * 5 && this.animationActive) { // 5回繰り返し
                        requestAnimationFrame(animate);
                    } else {
                        particle.remove();
                    }
                };
                
                animate();
            }

            highlightConnections(nodeId) {
                const node = this.nodes.get(nodeId);
                
                node.data.links.forEach(linkId => {
                    const connectionKey = nodeId < linkId ? `${nodeId}-${linkId}` : `${linkId}-${nodeId}`;
                    const connection = this.connections.get(connectionKey);
                    
                    if (connection) {
                        connection.element.style.background = 'rgba(255, 107, 107, 0.6)';
                        connection.element.style.height = '3px';
                    }
                });
            }

            clearHighlights() {
                this.nodes.forEach(node => {
                    node.element.classList.remove('highlighted');
                });
                
                this.connections.forEach(connection => {
                    connection.element.classList.remove('active');
                    connection.element.style.background = 'rgba(255, 255, 255, 0.3)';
                    connection.element.style.height = '2px';
                });
                
                document.getElementById('infoPanel').classList.remove('show');
                this.animationActive = false;
            }

            showNodeInfo(nodeData) {
                const infoPanel = document.getElementById('infoPanel');
                document.getElementById('infoTitle').textContent = nodeData.title;
                document.getElementById('infoContext').textContent = nodeData.context;
                infoPanel.classList.add('show');
            }

            startRenderLoop() {
                const update = () => {
                    this.handleKeyboardInput();
                    this.updateMinimap();
                    requestAnimationFrame(update);
                };
                update();
            }

            calculateWorldBounds() {
                let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                
                this.nodes.forEach(node => {
                    minX = Math.min(minX, node.x - node.size/2);
                    minY = Math.min(minY, node.y - node.size/2);
                    maxX = Math.max(maxX, node.x + node.size/2);
                    maxY = Math.max(maxY, node.y + node.size/2);
                });
                
                this.worldBounds = { minX, minY, maxX, maxY };
            }

            setupControls() {
                // マウスドラッグでのパン操作（改良版）
                this.container.addEventListener('mousedown', (e) => {
                    // ノードや検索パネルをクリックした場合は無視
                    if (e.target.classList.contains('node') || 
                        e.target.closest('.search-panel') || 
                        e.target.closest('.info-panel')) {
                        return;
                    }
                    
                    e.preventDefault();
                    this.isDragging = true;
                    this.lastMouseX = e.clientX;
                    this.lastMouseY = e.clientY;
                    this.container.style.cursor = 'grabbing';
                    document.body.style.userSelect = 'none';
                });

                document.addEventListener('mousemove', (e) => {
                    if (!this.isDragging) return;
                    
                    e.preventDefault();
                    const deltaX = e.clientX - this.lastMouseX;
                    const deltaY = e.clientY - this.lastMouseY;
                    
                    this.currentOffsetX += deltaX;
                    this.currentOffsetY += deltaY;
                    
                    this.lastMouseX = e.clientX;
                    this.lastMouseY = e.clientY;
                    
                    this.applyTransform();
                });

                document.addEventListener('mouseup', (e) => {
                    if (this.isDragging) {
                        e.preventDefault();
                        this.isDragging = false;
                        this.container.style.cursor = 'grab';
                        document.body.style.userSelect = '';
                    }
                });

                // タッチ操作対応（モバイル・タッチパッド）
                let lastTouchDistance = 0;
                let touchStartX = 0, touchStartY = 0;

                this.container.addEventListener('touchstart', (e) => {
                    if (e.touches.length === 1) {
                        // 単一タッチ - パン操作
                        touchStartX = e.touches[0].clientX;
                        touchStartY = e.touches[0].clientY;
                        this.isDragging = true;
                    } else if (e.touches.length === 2) {
                        // 2本指タッチ - ズーム準備
                        const touch1 = e.touches[0];
                        const touch2 = e.touches[1];
                        lastTouchDistance = Math.sqrt(
                            Math.pow(touch2.clientX - touch1.clientX, 2) +
                            Math.pow(touch2.clientY - touch1.clientY, 2)
                        );
                        this.isDragging = false;
                    }
                    e.preventDefault();
                });

                this.container.addEventListener('touchmove', (e) => {
                    e.preventDefault();
                    
                    if (e.touches.length === 1 && this.isDragging) {
                        // パン操作
                        const deltaX = e.touches[0].clientX - touchStartX;
                        const deltaY = e.touches[0].clientY - touchStartY;
                        
                        this.currentOffsetX += deltaX;
                        this.currentOffsetY += deltaY;
                        
                        touchStartX = e.touches[0].clientX;
                        touchStartY = e.touches[0].clientY;
                        
                        this.applyTransform();
                    } else if (e.touches.length === 2) {
                        // ピンチズーム
                        const touch1 = e.touches[0];
                        const touch2 = e.touches[1];
                        const currentDistance = Math.sqrt(
                            Math.pow(touch2.clientX - touch1.clientX, 2) +
                            Math.pow(touch2.clientY - touch1.clientY, 2)
                        );
                        
                        if (lastTouchDistance > 0) {
                            const centerX = (touch1.clientX + touch2.clientX) / 2;
                            const centerY = (touch1.clientY + touch2.clientY) / 2;
                            const zoomFactor = currentDistance / lastTouchDistance;
                            
                            const rect = this.container.getBoundingClientRect();
                            this.zoomAtPoint(centerX - rect.left, centerY - rect.top, zoomFactor);
                        }
                        
                        lastTouchDistance = currentDistance;
                    }
                });

                this.container.addEventListener('touchend', () => {
                    this.isDragging = false;
                    lastTouchDistance = 0;
                });

                // マウスホイールでのズーム（Mac/Windows両対応）
                this.container.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    
                    const rect = this.container.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    // Mac/Windows/Linuxでの差を吸収
                    let deltaY = e.deltaY;
                    
                    // Firefoxでの調整
                    if (e.deltaMode === 1) {
                        deltaY *= 40;
                    } else if (e.deltaMode === 2) {
                        deltaY *= 800;
                    }
                    
                    // macのスムーズスクロール対応
                    const sensitivity = Math.abs(deltaY) > 4 ? 0.002 : 0.02;
                    const zoomFactor = 1 - (deltaY * sensitivity);
                    
                    this.zoomAtPoint(mouseX, mouseY, zoomFactor);
                }, { passive: false });

                // キーボード操作（改良版）
                document.addEventListener('keydown', (e) => {
                    // 検索欄にフォーカスがある場合は無視
                    if (e.target.tagName === 'INPUT') return;
                    
                    const key = e.key.toLowerCase();
                    this.keys[key] = true;
                    
                    // ショートカットキー
                    if (e.ctrlKey || e.metaKey) {
                        switch (key) {
                            case '0':
                                e.preventDefault();
                                this.resetZoom();
                                break;
                            case '=':
                            case '+':
                                e.preventDefault();
                                this.zoomIn();
                                break;
                            case '-':
                                e.preventDefault();
                                this.zoomOut();
                                break;
                        }
                    }
                });

                document.addEventListener('keyup', (e) => {
                    if (e.target.tagName === 'INPUT') return;
                    this.keys[e.key.toLowerCase()] = false;
                });

                // 初期カーソル設定
                this.container.style.cursor = 'grab';
            }

            handleKeyboardInput() {
                // WASDキーでの移動速度を調整
                const baseSpeed = 15;
                const moveSpeed = baseSpeed / Math.max(0.5, this.currentScale);
                let moved = false;

                // WASD + 矢印キー対応
                if (this.keys['w'] || this.keys['arrowup']) {
                    this.currentOffsetY += moveSpeed;
                    moved = true;
                }
                if (this.keys['s'] || this.keys['arrowdown']) {
                    this.currentOffsetY -= moveSpeed;
                    moved = true;
                }
                if (this.keys['a'] || this.keys['arrowleft']) {
                    this.currentOffsetX += moveSpeed;
                    moved = true;
                }
                if (this.keys['d'] || this.keys['arrowright']) {
                    this.currentOffsetX -= moveSpeed;
                    moved = true;
                }

                // スペースキーで高速移動
                if (this.keys[' ']) {
                    const fastSpeed = moveSpeed * 2;
                    if (this.keys['w'] || this.keys['arrowup']) {
                        this.currentOffsetY += fastSpeed;
                    }
                    if (this.keys['s'] || this.keys['arrowdown']) {
                        this.currentOffsetY -= fastSpeed;
                    }
                    if (this.keys['a'] || this.keys['arrowleft']) {
                        this.currentOffsetX += fastSpeed;
                    }
                    if (this.keys['d'] || this.keys['arrowright']) {
                        this.currentOffsetX -= fastSpeed;
                    }
                }

                if (moved) {
                    this.applyTransform();
                }
            }

            zoomAtPoint(x, y, zoomFactor) {
                const newScale = Math.max(0.2, Math.min(3, this.currentScale * zoomFactor));
                
                if (newScale !== this.currentScale) {
                    const scaleDiff = newScale / this.currentScale;
                    
                    this.currentOffsetX = x - (x - this.currentOffsetX) * scaleDiff;
                    this.currentOffsetY = y - (y - this.currentOffsetY) * scaleDiff;
                    this.currentScale = newScale;
                    
                    this.applyTransform();
                }
            }

            zoomIn() {
                const centerX = window.innerWidth / 2;
                const centerY = window.innerHeight / 2;
                this.zoomAtPoint(centerX, centerY, 1.2);
            }

            zoomOut() {
                const centerX = window.innerWidth / 2;
                const centerY = window.innerHeight / 2;
                this.zoomAtPoint(centerX, centerY, 0.8);
            }

            resetZoom() {
                this.animateCamera(0, 0, 1);
            }

            setupMinimap() {
                this.updateMinimap();
                
                // ミニマップクリックで移動
                this.minimap.addEventListener('click', (e) => {
                    const rect = this.minimap.getBoundingClientRect();
                    const x = (e.clientX - rect.left) / rect.width;
                    const y = (e.clientY - rect.top) / rect.height;
                    
                    const worldX = this.worldBounds.minX + (this.worldBounds.maxX - this.worldBounds.minX) * x;
                    const worldY = this.worldBounds.minY + (this.worldBounds.maxY - this.worldBounds.minY) * y;
                    
                    const targetOffsetX = window.innerWidth / 2 - worldX;
                    const targetOffsetY = window.innerHeight / 2 - worldY;
                    
                    this.animateCamera(targetOffsetX, targetOffsetY, this.currentScale);
                });
            }

            updateMinimap() {
                this.minimap.innerHTML = '';
                
                // ミニマップノードを描画
                this.nodes.forEach(node => {
                    const minimapNode = document.createElement('div');
                    minimapNode.className = 'minimap-node';
                    
                    const x = ((node.x - this.worldBounds.minX) / (this.worldBounds.maxX - this.worldBounds.minX)) * 200;
                    const y = ((node.y - this.worldBounds.minY) / (this.worldBounds.maxY - this.worldBounds.minY)) * 150;
                    
                    minimapNode.style.left = (x - 2) + 'px';
                    minimapNode.style.top = (y - 2) + 'px';
                    
                    if (node.element.classList.contains('highlighted')) {
                        minimapNode.style.background = '#ff6b6b';
                        minimapNode.style.width = '6px';
                        minimapNode.style.height = '6px';
                    }
                    
                    this.minimap.appendChild(minimapNode);
                });
                
                // ビューポート矩形を描画
                const viewport = document.createElement('div');
                viewport.className = 'minimap-viewport';
                
                const viewWidth = window.innerWidth / this.currentScale;
                const viewHeight = window.innerHeight / this.currentScale;
                const viewX = (-this.currentOffsetX / this.currentScale) - viewWidth / 2;
                const viewY = (-this.currentOffsetY / this.currentScale) - viewHeight / 2;
                
                const minimapViewX = ((viewX - this.worldBounds.minX) / (this.worldBounds.maxX - this.worldBounds.minX)) * 200;
                const minimapViewY = ((viewY - this.worldBounds.minY) / (this.worldBounds.maxY - this.worldBounds.minY)) * 150;
                const minimapViewW = (viewWidth / (this.worldBounds.maxX - this.worldBounds.minX)) * 200;
                const minimapViewH = (viewHeight / (this.worldBounds.maxY - this.worldBounds.minY)) * 150;
                
                viewport.style.left = Math.max(0, Math.min(200 - minimapViewW, minimapViewX)) + 'px';
                viewport.style.top = Math.max(0, Math.min(150 - minimapViewH, minimapViewY)) + 'px';
                viewport.style.width = Math.min(200, minimapViewW) + 'px';
                viewport.style.height = Math.min(150, minimapViewH) + 'px';
                
                this.minimap.appendChild(viewport);
            }

            startRenderLoop() {
                // 必要に応じて継続的な描画処理を追加
            }
        }

        // グローバル関数
        function resetView() {
            graph.clearHighlights();
            graph.animateCamera(0, 0, 1);
            document.getElementById('searchInput').value = '';
            document.getElementById('searchResults').innerHTML = '';
        }

        function toggleAnimation() {
            graph.animationActive = !graph.animationActive;
        }

        function toggleHelp() {
            const helpPanel = document.getElementById('helpPanel');
            helpPanel.classList.toggle('show');
        }

        // 初期化
        const graph = new DynamicGraph();

        // ウィンドウリサイズ対応
        window.addEventListener('resize', () => {
            graph.clearHighlights();
            graph.container.innerHTML = '';
            graph.nodes.clear();
            graph.connections.clear();
            graph.createNodes();
            graph.createConnections();
            graph.calculateWorldBounds();
            graph.updateMinimap();
        });
    