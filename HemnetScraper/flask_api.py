from flask import Flask, request,render_template

# 1 create the flask env
app = Flask(__name__)
#Swagger(app)

# 2 Open the file 
pickle_in1 = open("scraper2.pkl","rb")
scraper2 = pickle.load(pickle_in1)

pickle_in2 = open("url_extractor.pkl","rb")
url_extractor = pickle.load(pickle_in2)

pickle_in3 = open("pct_change_metric.pkl","rb")
pct_change_metric = pickle.load(pickle_in3)

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/predict',methods=["GET"])
def predict():
    
    # Remember to add new parameters here: 
    area = request.args.get("area")
    keys = request.args.get("keys")
    min_year = request.args.get("min_year")
    current_url = request.args.get("current_url")
    relevant_only = request.args.get("relevant_only")
    sold_age = request.args.get("sold_age")
    loan_limit = request.args.get("loan_limit")

    current_url_new = url_extractor(area, keys, min_year )

    df = scraper2(current_url = current_url_new ,relevant_only = relevant_only ,sold_age = sold_age,loan_limit = int(loan_limit))

    
    return render_template('view.html',tables=[df.to_html(classes ='scraper')],
    titles = ['na', 'Results'])

@app.route('/comparison',methods=["GET"])
def compare_pct():
 
    # Remember to add new parameters here: 
     
    area = request.args.get("area")
    num_pages = request.args.get("num_pages")
    metric = request.args.get("metric")

    output = pct_change_metric(area = area, num_pages = num_pages , metric = metric )

    return output

if __name__=='__main__':
    app.run()
    