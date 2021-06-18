from matplotlib.animation import FFMpegWriter
import matplotlib.pyplot as plt
class Canvas():

    def __init__(self, fig, axes):
        self.fig = fig
        self.axes = axes
        self.fps =10
        view_port = 80
        self.view_port = view_port
        self.axes.set_xlim([-view_port, view_port])
        self.axes.set_ylim([-view_port, view_port])
        self.fig.canvas.draw()
        self.report_text = None
        background = fig.canvas.copy_from_bbox(axes.bbox)
        self.writer = None

    def set_view_port(self, view_port):
        self.view_port = view_port
        self.axes.set_xlim([-view_port, view_port])
        self.axes.set_ylim([-view_port, view_port])
        self.fig.canvas.draw()

    def saving(self, dpi=100, fps=10):
        self.fps = fps
        self.writer = FFMpegWriter(fps=self.fps)
        self.writer.setup(self.fig, "writer_test.mp4", dpi)

    def write(self):
        if self.writer is None:
            raise ValueError("writer has not been initialised, try calling Canvas.saving()")
        self.writer.grab_frame()

    def finish(self):
        if self.writer is None:
            raise ValueError("writer has not been initialised, try calling Canvas.saving()")
        self.writer.finish()
        #self.writer.cleanup()

    def report(self, messages):
        if self.report_text is None:
            self.report_text = []
            x_pos = -self.view_port*0.95
            y_pos = self.view_port*0.95
            for msg in messages:
                self.report_text.append(plt.text(x_pos, y_pos, "{}: {:.0f}".format(msg[0], msg[1])))
                y_pos -= self.view_port*0.05
        else:
            for i_msg, msg in enumerate(messages):
                text = self.report_text[i_msg]
                text.set_text("{}: {:.0f}".format(msg[0], msg[1]))
