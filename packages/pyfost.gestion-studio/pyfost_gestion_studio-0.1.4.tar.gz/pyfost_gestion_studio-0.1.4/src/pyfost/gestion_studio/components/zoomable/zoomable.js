// zoomable.js
export default {
    name: 'ZoomableContainer',
    props: {
        border_width: {
            type: String,
            default: '2px',
        },
        border_color: {
            type: String,
            default: '#888888',
        },
        initialWidthProp: {
            type: Number,
            default: 800,
        },
        initialHeightProp: {
            type: Number,
            default: 400,
        },
        options: Object,
    },
    template: `
      <div 
        ref="zoomableContainer"
        :style="containerStyle"
        class="zoomable p-0"
        @wheel="handleWheel"
        @mousedown="handleMouseDown"
      >
        <div class="zoom-content" :style="zoomContentStyle" class="grow">
          <slot></slot>
        </div>
      </div>
    `,
    data() {
        return {
            // --- Resizing Properties ---
            currentWidth: this.initialWidthProp,
            currentHeight: this.initialHeightProp,
            resizeStep: 50,
            minWidth: 150,
            minHeight: 100,
            maxWidth: 2000,
            maxHeight: 1000,

            // --- Drag Resizing 
            isResizing: false,
            startX: 0,
            startY: 0,
            startW: 0,
            startH: 0,

        };
    },
    watch: {
        initialWidthProp(newVal) {
            this.currentWidth = newVal;
        },
        initialHeightProp(newVal) {
            this.currentHeight = newVal;
        },
    },

    // Lifecycle hooks
    // created() {
    // Data properties are already initialized using props directly in data()
    // If you didn't use props for initial values:
    // this.currentWidth = 400;
    // this.currentHeight = 300;
    // this.zoom_level = 1.0;
    // },

    // mounted() {
    //   // console.log('Zoomable mounted with options:', this.options);
    //   // Example: if attaching global listeners
    //   // window.addEventListener('keydown', this.handleGlobalKeyDown);
    // },

    // beforeDestroy() {
    //   // Example: if removing global listeners
    //   // window.removeEventListener('keydown', this.handleGlobalKeyDown);
    // },

    computed: {
        containerStyle() {
            return {
                'border': `${this.border_width} solid ${this.border_color}`,
                width: `${this.currentWidth}px`,
                height: `${this.currentHeight}px`,
                cursor: 'se-resize',
                overflow: 'hidden',
            };
        },
        zoomContentStyle() {
            return {
                transform: `scale(${this.zoom_level})`,
                transformOrigin: "center center",
                transition: "transform 0.2s ease-out",
            };
        },
    },

    methods: {
        emit_size_changed() {
            const eventData = {
                width: this.currentWidth,
                height: this.currentHeight,
            };
            this.$emit('sizeChanged', eventData);
        },
        handleWheel(event) {
            event.preventDefault();
            const delta = Math.sign(event.deltaY);
            console.log('Zoomable Wheel', delta, event.deltaY, '!');
            if (delta < 0) {
                this.currentWidth = Math.min(this.maxWidth, this.currentWidth + this.resizeStep);
                this.currentHeight = Math.min(this.maxHeight, this.currentHeight + this.resizeStep);
            } else if (delta > 0) {
                this.currentWidth = Math.max(this.minWidth, this.currentWidth - this.resizeStep);
                this.currentHeight = Math.max(this.minHeight, this.currentHeight - this.resizeStep);
            }

            this.emit_size_changed();

        },

        handleMouseDown(event) {
            this.isResizing = true;
            this.startX = event.clientX;
            this.startY = event.clientY;
            this.startW = this.currentWidth;
            this.startH = this.currentHeight;


            window.addEventListener('mousemove', this.handleMouseMove);
            window.addEventListener('mouseup', this.handleMouseUp);
            event.preventDefault(); // Prevent text selection during drag

        },
        handleMouseMove(event) {
            if (!this.isResizing) return;

            const dx = event.clientX - this.startX;
            const dy = event.clientY - this.startY;

            const sensitivity = 1.0;

            this.currentWidth = Math.min(this.maxWidth, this.startW + dx * sensitivity);
            this.currentHeight = Math.max(this.minHeight, this.startH + dy * sensitivity);
        },

        handleMouseUp(event) {
            if (!this.isResizing) return;
            this.isResizing = false;

            this.emit_size_changed();

            window.removeEventListener('mousemove', this.handleMouseMove);
            window.removeEventListener('mouseup', this.handleMouseUp);
        },
    },
};