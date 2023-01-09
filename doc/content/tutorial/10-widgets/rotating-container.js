// rotating-container.js

class RotatingContainer {
    constructor(lona_window) {
        this.lona_window = lona_window;
    }

    animate(time) {
        const container = this.root_node;

        this.angle = this.angle += this.data['animation_speed'];

        if(this.angle >= 360) {
            this.angle = 0;
        }

        container.style['transform'] = `rotate(${this.angle}deg)`;

        if(this.data['animation_running']) {
            requestAnimationFrame(time => {
                this.animate(time);
            });
        }
    }

    // gets called on initial setup
    setup() {
        this.angle = 0;

        if(this.data['animation_running']) {
            requestAnimationFrame(time => {
                this.animate(time);
            });
        }
    }

    // gets called every time the data gets updated
    data_updated() {
        if(this.data['animation_running']) {
            requestAnimationFrame(time => {
                this.animate(time);
            });
        }
    }

    // gets called when the widget gets destroyed
    deconstruct() {

    }
}


// register widget class with the same name we used
// in `RotatingContainer.WIDGET`
Lona.register_widget_class('RotatingContainer', RotatingContainer);
