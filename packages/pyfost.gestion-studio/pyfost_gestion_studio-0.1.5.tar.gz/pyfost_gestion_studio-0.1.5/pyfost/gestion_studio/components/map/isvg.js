// isvg.js
export default {
    props: {
        svgContent: {
            type: String,
            required: true,
        },
        idStyles: {
            type: Object,
            default: () => ({}),
        },
        classStyles: {
            type: Object,
            default: () => ({}),
        },
        fitViewRequest: {
            type: Number,
            default: 0.0,
        },
        panningEnabled: {
            type: Boolean,
            default: false,
        },
        clickableElementsQuery: { // CSS selector for which elements are clickable
            type: String,
            default: null, // If null, all elements inside SVG are potentially clickable
        }
    },
    template: `
        <div 
          ref="containerElement"
          :class="containerClass"
          >
          <div ref="svgContainer"
            class="svg-hover-area"
            v-html="svgContent"
            @click="handleSvgClick"
            @mouseover="handleMouseOver"
            @mousedown="handleMouseDown"
            @wheel="handleWheel"
            >
          </div>
        </div>
    `,

    data() {
        return {
            componentId: Math.random().toString(36).substring(2, 2 + 9), // unique ID for each component instance
            isPanning: false,
            zoomLevel: 1.0,
            startX: 0,
            startY: 0,
            initialViewBox: { x: 0, y: 0, width: 0, height: 0 },
            svgElement: null, // To store the reference to the <svg> element

            // initialWidth: 500,
            // initialHeight: 500,
            // resizeStep: 50,
            // minWidth: 200,
            // minHeight: 200,
            // // Reactive State
            // currentWidth: 300, // Initialize with initialWidth
            // currentHeight: 200, // Initialize with initialHeight

        };
    },

    computed: {
        containerClass() {
            return `svg-container-${this.componentId}`;
        },
        // resizableElementStyle() {
        //     return {
        //         // width: `${this.currentWidth}px`,
        //         // height: `${this.currentHeight}px`,
        //         border: '2px dashed #4CAF50',
        //         backgroundColor: 'lightgoldenrodyellow',
        //         // display: 'flex',
        //         // flexDirection: 'column',
        //         // alignItems: 'center',
        //         // justifyContent: 'center',
        //         overflow: 'hidden',
        //         cursor: 'ns-resize',
        //         userSelect: 'none',
        //         transition: 'width 0.1s ease-out, height 0.1s ease-out',
        //     };
        // },
    },

    watch: {
        svgContent: {
            immediate: true, // Run this watcher also when the component is first created
            handler(newVal, oldVal) {
                this.$nextTick(() => { // Ensure v-html has updated the DOM
                    this.findAndPrepareSvgElement();
                    this.applyAllStyles();
                });
            }
        },
        idStyles: {
            handler(newStyles) {
                this.$nextTick(() => {
                    this.applyIdStyles(newStyles);
                });
            },
            deep: true,
        },
        classStyles: {
            handler(newStyles) {
                this.$nextTick(() => {
                    this.applyClassStyles(newStyles);
                    this.fitView();
                });
            },
            deep: true,
        },
        fitViewRequest: {
            handler(newValue) {
                this.$nextTick(() => {
                    this.fitView();
                });
            },
        },
        panningEnabled(newValue) {
            if (this.$refs.svgContainer) {
                this.$refs.svgContainer.style.cursor = newValue ? 'grab' : 'default';
            }
        }
    },


    mounted() {
        this.mount_component_style();
        // Initial setup already handled by immediate watcher for svgContent
        // Add global mouse move and up listeners here if needed for robustness,
        // but for now, we'll add them on mousedown.
        if (this.$refs.svgContainer && this.panningEnabled) {
            this.$refs.svgContainer.style.cursor = 'grab';
        }
    },

    beforeUnmount() {
        this.unmount_component_style();
        // Clean up global event listeners if they were added to window
        window.removeEventListener('mousemove', this.handleMouseMove);
        window.removeEventListener('mouseup', this.handleMouseUp);
    },


    methods: {
        mount_component_style() {
            const style = document.createElement('style');
            style.setAttribute('data-component', 'svg-hover');
            style.textContent = `
              .svg-container-${this.componentId} .svg-hover-area svg * {
                transition: stroke 0.3s ease, stroke-width 0.3s ease;
              }
                            
              .svg-container-${this.componentId} .zone.isvg_hovered, .seat.isvh_hovered  {
                stroke: red !important;
                stroke-width: 3px !important;
              }
            `;

            document.head.appendChild(style);
            this.dynamicStyle = style;
        },

        unmount_component_style() {
            if (this.dynamicStyle) {
                document.head.removeChild(this.dynamicStyle);
            }
        },

        findAndPrepareSvgElement() {
            if (this.$refs.svgContainer) {
                this.svgElement = this.$refs.svgContainer.querySelector('svg');
                this.currentWidth = this.svgElement.clientWidth;
                this.currentHeight = this.svgElement.clientHeight;
                console.log(this.currentHeight, this.currentWidth);

                if (this.svgElement) {
                    const viewBox = this.svgElement.getAttribute('viewBox');
                    console.log('[ISVG] Reading Initial ViewBox:', viewBox);
                    if (viewBox) {
                        const parts = viewBox.split(' ').map(Number);
                        if (parts.length === 4) {
                            this.initialViewBox = { x: parts[0], y: parts[1], width: parts[2], height: parts[3] };
                        } else {
                            console.warn('[ISVG] Invalid viewBox format on SVG:', viewBox);
                            // this.initialViewBox = { x: 0, y: 0, width: parseFloat(this.svgElement.getAttribute('width')), height: parseFloat(this.svgElement.getAttribute('height')) }; // Fallback
                            this.initialViewBox = { x: 0, y: 0, width: this.currentWidth, height: this.currentHeight }; // Fallback
                        }
                    } else {
                        // If no viewBox, try to set a default one based on width/height attributes
                        // This is essential for panning via viewBox to work.
                        const width = parseFloat(this.svgElement.getAttribute('width'));
                        const height = parseFloat(this.svgElement.getAttribute('height'));
                        if (!isNaN(width) && !isNaN(height)) {
                            this.svgElement.setAttribute('viewBox', `0 0 ${this.currentWidth} ${this.currentHeight}`);
                            this.initialViewBox = { x: 0, y: 0, width: width, height: height };
                            // console.log('[ISVG] Applied default viewBox:', `0 0 ${width} ${height}`);
                        } else {
                            console.warn('[ISVG] SVG has no viewBox and no width/height attributes for default. Panning might not work as expected.');
                            // Fallback for initialViewBox if everything else fails
                            this.initialViewBox = { x: 0, y: 0, width: 300, height: 200 }; // Arbitrary fallback
                        }
                    }
                } else {
                    console.warn('[ISVG] No <svg> element found inside the container.');
                }
                console.log('[ISVG] Initial ViewBox:', this.initialViewBox);
            }
        },

        handleMouseOver(event) {
            // Check if the target is an SVG element (not the container)
            if (event.target.tagName && this.isSvgElement(event.target)) {
                // Remove hover class from previously isvg_hovered element
                if (this.currentHoveredElement && this.currentHoveredElement !== event.target) {
                    this.currentHoveredElement.classList.remove('isvg_hovered');
                }

                // Add hover class to current element
                event.target.classList.add('isvg_hovered');
                this.currentHoveredElement = event.target;
            }
        },

        handleMouseOut(event) {
            // Only remove class if we're leaving the element (not entering a child)
            if (event.target.tagName && this.isSvgElement(event.target)) {
                // Check if we're moving to a child element
                if (!event.target.contains(event.relatedTarget)) {
                    event.target.classList.remove('isvg_hovered');
                    if (this.currentHoveredElement === event.target) {
                        this.currentHoveredElement = null;
                    }
                }
            }
        },

        isSvgElement(element) {
            // List of SVG element tag names
            const svgElements = ['circle', 'rect', 'polygon', 'path', 'line', 'ellipse', 'polyline', 'text', 'g'];
            return svgElements.includes(element.tagName.toLowerCase());
        },

        handleMouseDown(event) {
            // Priority to click handling if the target matches clickableElementsQuery
            let clickTargetMatch = false;
            if (this.clickableElementsQuery && event.target) {
                let currentElement = event.target;
                while (currentElement && currentElement !== this.$refs.svgContainer && currentElement !== document.body) {
                    if (currentElement.matches && currentElement.matches(this.clickableElementsQuery)) {
                        clickTargetMatch = true;
                        break;
                    }
                    currentElement = currentElement.parentElement;
                }
            }
            // If the click is specifically for an interactive element, don't initiate panning.
            if (clickTargetMatch && event.button === 0) { // event.button === 0 is left click
                // The handleSvgClick method will be called by the @click handler.
                // We don't want to start panning if a clickable element was the primary target.
                return;
            }


            if (!this.panningEnabled || event.button !== 0) return; // Only pan on left click
            if (!this.svgElement) {
                this.findAndPrepareSvgElement(); // Try to find it again if not found initially
                if (!this.svgElement) return;
            }

            this.isPanning = true;
            this.startX = event.clientX;
            this.startY = event.clientY;

            // Update initialViewBox from the current state of the SVG element,
            // as it might have been changed by previous pans or other manipulations.
            const currentViewBoxAttr = this.svgElement.getAttribute('viewBox');
            if (currentViewBoxAttr) {
                const parts = currentViewBoxAttr.split(' ').map(Number);
                if (parts.length === 4) {
                    this.initialViewBox = { x: parts[0], y: parts[1], width: parts[2], height: parts[3] };
                }
            } // else, we stick with the last known this.initialViewBox

            this.$refs.svgContainer.style.cursor = 'grabbing';

            // Add listeners to window for smoother panning even if mouse leaves component
            window.addEventListener('mousemove', this.handleMouseMove);
            window.addEventListener('mouseup', this.handleMouseUp);

            event.preventDefault(); // Prevent text selection during drag
            event.stopPropagation(); // Prevent parent to receive the event
        },

        handleMouseMove(event) {
            if (!this.isPanning || !this.svgElement) return;

            const dx = event.clientX - this.startX;
            const dy = event.clientY - this.startY;

            // Sensitivity factor (how much the viewBox moves relative to mouse movement)
            // This depends on the SVG's own coordinate system and its display size.
            // If the SVG is scaled, you might need to adjust this.
            // For a 1:1 pixel mapping initially, a sensitivity of 1 is direct.
            // If your SVG content is "zoomed out" (viewBox width/height larger than display width/height),
            // a higher sensitivity might feel more natural.
            // Let's assume the viewBox dimensions represent the "true" size for now.
            const sensitivity = 1.0 * this.zoomLevel; // Adjust as needed

            // New viewBox X and Y
            // We move the viewBox in the OPPOSITE direction of the mouse drag
            const newX = this.initialViewBox.x - dx * sensitivity;
            const newY = this.initialViewBox.y - dy * sensitivity;

            this.svgElement.setAttribute('viewBox', `${newX} ${newY} ${this.initialViewBox.width} ${this.initialViewBox.height}`);
        },

        handleMouseUp(event) {
            if (!this.isPanning) return;
            this.isPanning = false;
            if (this.$refs.svgContainer) { // Check if container still exists
                this.$refs.svgContainer.style.cursor = this.panningEnabled ? 'grab' : 'default';
            }

            window.removeEventListener('mousemove', this.handleMouseMove);
            window.removeEventListener('mouseup', this.handleMouseUp);
        },

        handleWheel(event) {
            // console.log('isvg WHEEL');
            event.stopPropagation();
            event.preventDefault();

            const delta = Math.sign(event.deltaY);
            if (delta > 0) {
                this.applyZoom(this.zoomLevel + .1);
            } else if (delta < 0) {
                this.applyZoom(this.zoomLevel - .1);
            }
        },

        fitView() {
            console.log('FIT VIEW');
            this.svgElement.setAttribute('viewBox', `0 0 ${this.currentWidth} ${this.currentHeight}`);
            this.applyZoom(1.0);
        },
        zoomIn() {
            this.zoomLevel += 0.1;
            this.applyZoom(this.zoomLevel);
        },
        zoomOut() {
            this.zoomLevel -= 0.1;
            this.applyZoom(this.zoomLevel);
        },
        applyZoom(zoomLevel) {
            const sensitivity = 5; // Adjust as needed
            zoomLevel = Math.max(zoomLevel, .1);
            zoomLevel = Math.min(zoomLevel, 4);
            this.zoomLevel = zoomLevel;
            console.log('VIEWBOX ZOOM:', this.zoomLevel);

            // Update initialViewBox from the current state of the SVG element,
            // as it might have been changed by previous pans or other manipulations.
            const currentViewBoxAttr = this.svgElement.getAttribute('viewBox');
            if (currentViewBoxAttr) {
                const parts = currentViewBoxAttr.split(' ').map(Number);
                if (parts.length === 4) {
                    this.initialViewBox = { x: parts[0], y: parts[1], width: parts[2], height: parts[3] };
                }
            } // else, we stick with the last known this.initialViewBox

            const x = this.initialViewBox.x;
            const y = this.initialViewBox.y;
            const width = parseFloat(this.svgElement.getAttribute('width'));
            const height = parseFloat(this.svgElement.getAttribute('height'));
            const newW = width * (this.zoomLevel * sensitivity);
            const newH = height * (this.zoomLevel * sensitivity);

            this.svgElement.setAttribute('viewBox', `${x} ${y} ${newW} ${newH}`);

        },

        applyAllStyles() {
            if (!this.$refs.svgContainer) return;
            this.applyIdStyles(this.idStyles);
            this.applyClassStyles(this.classStyles);
        },

        applyStylesToElements(elements, styleProps) {
            if (elements.length > 0) {
                elements.forEach((element) => {
                    for (const prop in styleProps) {
                        if (prop === 'textContent' && typeof element.textContent !== 'undefined') {
                            element.textContent = styleProps[prop];
                        } else {
                            element.setAttribute(prop, styleProps[prop]);
                        }
                    }
                });
            }
        },

        applyIdStyles(stylesToApply) {
            if (!this.$refs.svgContainer || !stylesToApply) return;
            for (const id in stylesToApply) {
                const element = this.$refs.svgContainer.querySelector(`#${id}`);
                if (element) {
                    this.applyStylesToElements([element], stylesToApply[id]);
                } else {
                    console.warn(`[ISVG] Element with ID "${id}" not found.`);
                }
            }
        },

        applyClassStyles(stylesToApply) {
            if (!this.$refs.svgContainer || !stylesToApply) return;
            for (const className in stylesToApply) {
                const elements = Array.from(this.$refs.svgContainer.querySelectorAll(`.${className}`));
                if (elements.length > 0) {
                    this.applyStylesToElements(elements, stylesToApply[className]);
                }
            }
        },

        updateTextContent(elementId, newText) {
            if (!this.$refs.svgContainer) return;
            const textElement = this.$refs.svgContainer.querySelector(`#${elementId}`);
            if (textElement && typeof textElement.textContent !== 'undefined') {
                textElement.textContent = newText;
            } else {
                console.warn(`[ISVG] Text element with ID "${elementId}" not found or does not support textContent.`);
            }
        },

        handleSvgClick(event) {
            let targetElement = event.target;

            // If a clickableElementsQuery is provided, check if the target or its parents match
            if (this.clickableElementsQuery) {
                if (!targetElement.matches(this.clickableElementsQuery)) {
                    // If the direct target doesn't match, check its parents up to the SVG container
                    let parent = targetElement.parentElement;
                    while (parent && parent !== this.$refs.svgContainer) {
                        if (parent.matches(this.clickableElementsQuery)) {
                            targetElement = parent; // Found a matching parent
                            break;
                        }
                        parent = parent.parentElement;
                    }
                    // If no matching parent found and target itself doesn't match, ignore click
                    if (!targetElement.matches(this.clickableElementsQuery)) {
                        // console.debug('[ISVG] Clicked element does not match clickableElementsQuery:', event.target);
                        return;
                    }
                }
            } else {
                // If no query, ensure the click is within an actual SVG element, not the div container itself.
                // This check can be refined. If the div itself *is* the svg root, this is fine.
                // If svgContent is like "<svg>...</svg>", then targetElement should be inside.
                if (targetElement === this.$refs.svgContainer && targetElement.children.length > 0 && targetElement.children[0].tagName.toLowerCase() === 'svg') {
                    // Click was on the container div, but we want clicks on SVG elements themselves.
                    // This might happen if the SVG doesn't fill the whole div.
                    // Or, if we want to ignore clicks on the "background" of the SVG.
                    // console.debug('[ISVG] Clicked on SVG container, not an element within.');
                    // return; // Uncomment if you want to ignore clicks on the div background
                }
            }


            // Ensure we have an element (it might be the main SVG element itself)
            if (targetElement && targetElement.tagName) {
                // console.log(targetElement);
                // console.log(targetElement.children);
                const elementInfo = {
                    id: targetElement.id || null,
                    tagName: targetElement.tagName.toLowerCase(),
                    classList: Array.from(targetElement.classList || []),
                    // You can add more properties from the event or element if needed
                    // For example, to get attributes:
                    // attributes: Array.from(targetElement.attributes).reduce((obj, attr) => {
                    //   obj[attr.name] = attr.value;
                    //   return obj;
                    // }, {}),
                };
                // Emit an event that NiceGUI can listen to
                this.$emit('element_click', elementInfo);
            }
        }
    },
};
