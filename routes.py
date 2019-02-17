from flask import Flask, render_template
from brush_info import get_usage_data, calculate_group_dynamics
from operator import itemgetter

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    usage_data = get_usage_data()
    group_data = sorted(calculate_group_dynamics(usage_data), key=itemgetter(3), reverse=True)
    return render_template("home.html", usage_data=usage_data, group_data=group_data)


if __name__ == "__main__":
    app.run(debug=False)
