from flask import Flask,request, abort, make_response, jsonify
from flask_cors import CORS
import traceback
# from flask_ngrok2 import run_with_ngrok
from model.user_model import user_model
# from flask import jsonify
from flask_socketio import SocketIO, emit
# from flask_ngrok2 import run_with_ngrok
from apscheduler.schedulers.background import BackgroundScheduler
from controllers.connection_verifier import ConnectionVerifier
from model.demo_display_model import demo_display_unit_model
import signal, sys
# app = Flask(__name__)

verifier = None

def create_app():
    app = Flask(__name__)
    
    from controllers.demo_display_controller import register_controllers
    register_controllers(app)
    
    return app

# from controllers import demo_display_controller

app = create_app()

CORS(app, origins=["*"], supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
scheduler = BackgroundScheduler()

# run_with_ngrok(app)
# obj1=user_model()


demo_display_unit_model_obj = demo_display_unit_model()
con2 = demo_display_unit_model_obj.get_con2()
# @app.before_first_request
def start_verifier():
    global verifier
    verifier = ConnectionVerifier(con2)
    verifier.start()

# @app.route('/stop_verifier')
# def stop_verifier():
#     global verifier
#     verifier.stopped = True
#     return 'Stopped the verifier'

# @app.teardown_appcontext
# def teardown_app_context(exception):
#     print("####### Close the flask app #######")
#     global verifier
#     if verifier:
#         verifier.stopped = True

def signal_handler(sig, frame):
    # global app_running
    # app_running = False
    global verifier
    if verifier:
        verifier.stopped = True
    print('Flask app stopped manually')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)




@app.route("/")
def welcome():
    con2.close()
    return "avfcHedsalkllo"

@app.route("/home")
def home():
    return "myhokjme"
# WebSocket event handler
latest_result = {"data": None}

latest_data = None

###################################################################
def getworkforoperator_model(self):
    try:
        
        
        # month = data.get('month')
        # date = data.get('date')

        # current_date = datetime.now()

        # Extract the month and date
        # month = current_date.strftime('%m')
        # date = current_date.strftime('%d')

        # Construct and execute the query
        query = "SELECT * FROM work_f1 WHERE DATE(STR_TO_DATE(timestamp, '%W, %M %d, %Y %H:%i:%s')) = CURDATE()"

        with con2.cursor(dictionary=True) as cur2:
            if not con2.is_connected():
                con2.reconnect()

            cur2.execute(query)
            result = self.cur2.fetchall()
            print(result)
        
            if result is not None:



                for entry in result:
                    station_id = entry["station_id"]
                    split_items = station_id.split()
                    # print(split_items)
                    if len(split_items) == 3:
                        F1, L1, S1 = split_items

                # Further split each part
                        F1_part1, F1_part2 = F1[0], F1[1:]
                        L1_part1, L1_part2 = L1[0], L1[1:]
                        S1_part1, S1_part2 = S1[0], S1[1:]

                        # print("F1:", F1_part1, F1_part2)
                        # print("L1:", L1_part1, L1_part2)
                        # print("S1:", S1_part1, S1_part2)                
                    # station_num = "".join(filter(str.isdigit, station_id_parts[-1]))

                    entry["station_num"] = S1_part2
                # print(result)
                res = make_response({"processdata": result},200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                res.headers['Content-Type'] = 'application/json'
                # print(res)
                return res

            else:
                res = make_response({"processdata":"No Data Found"},201)
                res.headers['Access-Control-Allow-Origin'] = "*"
                res.headers['Content-Type'] = 'application/json'
                return res
    except Exception as e:
        print(e)
        traceback.print_exc()
        res = make_response({"processdata":"got error"},202)
        res.headers['Access-Control-Allow-Origin'] = "*"
        res.headers['Content-Type'] = 'application/json'            
        return res
    
###################################################################
# Method to update the latest data
def update_latest_data():
    global latest_data
    response = getworkforoperator_model()
    result = response.json
    latest_data = result['processdata']

# WebSocket event handler
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Update the latest data when a client connects
    update_latest_data()
    # Emit the latest data to the client
    if latest_data is not None:
        socketio.emit('update_work_for_operator', {'data': latest_data})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Background task for periodic updates
# Background task for periodic updates
# Background task for periodic updates
def scheduled_task():
    print("Entering scheduled_task")
    with app.app_context():
        global latest_data
        try:
            print("latest_data:", latest_data)
            update_latest_data()
            if latest_data is not None:
                print("Emitting message to clients")
                socketio.emit('update_work_for_operator', {'data': latest_data})
        except Exception as e:
            print(f"Error in scheduled_task: {e}")


# Start the background task when the server starts
scheduler.add_job(scheduled_task, 'interval', seconds=5)
scheduler.start()

if __name__ == '__main__':
    start_verifier()
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)
    # app.run(host='0.0.0.0', port=5000)
