import time

from lona.html.nodes import Div, H2, Button


def foo(request):
    colors = ['blue', 'red', 'green', 'grey']
    style = {
        'float': 'left',
        'margin': '3px',
        'width': '50px',
        'height': '50px',
        'background-color': colors[0],
        'cursor': 'pointer',
    }

    html = Div(
        H2('Squares'),
        Div(style=style, clickable=True),
        Div(style=style, clickable=True),
        Div(style=style, clickable=True),
        Div(style=style, clickable=True),
        Div(style=style, clickable=True),
    )

    while True:
        event = request.client.await_user_input(html)

        if event.node == html.nodes[-1]:
            return 'closed'

        if event.name == 'click':
            next_color = \
                colors[colors.index(event.node.style['background-color'])-1]

            event.node.style['background-color'] = next_color


class bar:
    colors = ['blue', 'red', 'green', 'grey']

    def handle_request(self, request):
        style = {
            'float': 'left',
            'margin': '3px',
            'width': '50px',
            'height': '50px',
            'background-color': self.colors[0],
            'cursor': 'pointer',
        }

        html = Div(
            H2('Squares'),
            Div(style=style, clickable=True),
            Div(style=style, clickable=True),
            Div(style=style, clickable=True),
            Div(style=style, clickable=True),
            Div(style=style, clickable=True),
        )

        self.html = html

        for i in range(60):
            html.nodes[0].set_text('Squares {}'.format(i))
            request.client.show_html(html)
            time.sleep(1)

    def handle_input_event(self, input_event):
        next_color = self.colors[self.colors.index(input_event.node.style['background-color'])-1]
        input_event.node.style['background-color'] = next_color





from lona.html.forms import *


class MyForm(Form):
    username = TextField(label='Username')
    full_name = TextField(label='Full Name', placeholder='full name')
    favorite_color = ColorField(label='Color', default='#00ff00')
    checkbox = CheckboxField()

    def check(self):
        username = self.clean_values['username']

        if len(username) > 3:
            self.add_error('username', 'to long')


def form_view(request):
    form = MyForm(initial={'username': 'fsc'})

    html = Div(
        H2('Form Test'),
        form,
    )

    while True:
        request.client.await_user_input(html)

        import IPython
        IPython.embed()


from lona.html.grid import *
from lona.html.nodes import Div

def grid_view(request):

    html = Div(
        Row(
            Col6('Foo'),
            Col6('Bar'),
        ),
        Row(
            Col6('Foo'),
            Col6('Bar'),
        ),

        Div('baz'),
    )

    request.client.show_html(html)


def sort(request):
    from lona.html.widgets import SortableTable

    table_data = [
        # source https://worldpopulationreview.com/world-cities

        ['Rank', 'Name', 'Country', '2020 Population', '2019 Population', 'Change'],

        ['1', 'Tokyo', 'Japan', '37,393,128', '37,435,192', '-0.11%'],
        ['2', 'Delhi', 'India', '30,290,936', '29,399,140', '3.03%'],
        ['3', 'Shanghai', 'China', '27,058,480', '26,317,104', '2.82%'],
        ['4', 'Sao Paulo', 'Brazil', '22,043,028', '21,846,508', '0.90%'],
        ['5', 'Mexico City', 'Mexico', '21,782,378', '21,671,908', '0.51%'],
        ['6', 'Dhaka', 'Bangladesh', '21,005,860', '20,283,552', '3.56%'],
        ['7', 'Cairo', 'Egypt', '20,900,604', '20,484,964', '2.03%'],
        ['8', 'Beijing', 'China', '20,462,610', '20,035,456', '2.13%'],
        ['9', 'Mumbai', 'India', '20,411,274', '20,185,064', '1.12%'],
        ['10', 'Osaka', 'Japan', '19,165,340', '19,222,664', '-0.30%'],
        ['11', 'Karachi', 'Pakistan', '16,093,786', '15,741,406', '2.24%'],
        ['12', 'Chongqing', 'China', '15,872,179', '15,354,067', '3.37%'],
        ['13', 'Istanbul', 'Turkey', '15,190,336', '14,967,667', '1.49%'],
        ['14', 'Buenos Aires', 'Argentina', '15,153,729', '15,057,273', '0.64%'],
        ['15', 'Kolkata', 'India', '14,850,066', '14,755,186', '0.64%'],
        ['16', 'Lagos', 'Nigeria', '14,368,332', '13,903,620', '3.34%'],
        ['17', 'Kinshasa', 'Democratic Republic Of The Congo', '14,342,439', '13,743,278', '4.36%'],
        ['18', 'Manila', 'Philippines', '13,923,452', '13,698,889', '1.64%'],
        ['19', 'Tianjin', 'China', '13,589,078', '13,396,402', '1.44%'],
        ['20', 'Rio De Janeiro', 'Brazil', '13,458,075', '13,374,275', '0.63%'],
        ['21', 'Guangzhou', 'China', '13,301,532', '12,967,862', '2.57%'],
        ['22', 'Lahore', 'Pakistan', '12,642,423', '12,188,196', '3.73%'],
        ['23', 'Moscow', 'Russian Federation', '12,537,954', '12,476,171', '0.50%'],
        ['24', 'Shenzhen', 'China', '12,356,820', '12,128,721', '1.88%'],
        ['25', 'Bangalore', 'India', '12,326,532', '11,882,666', '3.74%'],
        ['26', 'Paris', 'France', '11,017,230', '10,958,187', '0.54%'],
        ['27', 'Bogota', 'Colombia', '10,978,360', '10,779,376', '1.85%'],
        ['28', 'Chennai', 'India', '10,971,108', '10,711,243', '2.43%'],
        ['29', 'Jakarta', 'Indonesia', '10,770,487', '10,638,689', '1.24%'],
        ['30', 'Lima', 'Peru', '10,719,188', '10,554,712', '1.56%'],
        ['31', 'Bangkok', 'Thailand', '10,539,415', '10,350,204', '1.83%'],
        ['32', 'Hyderabad', 'India', '10,004,144', '9,741,397', '2.70%'],
        ['33', 'Seoul', 'Republic Of Korea', '9,963,452', '9,962,393', '0.01%'],
        ['34', 'Nagoya', 'Japan', '9,552,132', '9,532,059', '0.21%'],
        ['35', 'London', 'United Kingdom', '9,304,016', '9,176,530', '1.39%'],
        ['36', 'Chengdu', 'China', '9,135,768', '8,971,839', '1.83%'],
        ['37', 'Tehran', 'Iran (Islamic Republic Of)', '9,134,708', '9,013,663', '1.34%'],
        ['38', 'Nanjing', 'China', '8,847,372', '8,545,577', '3.53%'],
        ['39', 'Ho Chi Minh City', 'Viet Nam', '8,602,317', '8,371,428', '2.76%'],
        ['40', 'Wuhan', 'China', '8,364,977', '8,266,273', '1.19%'],
        ['41', 'Luanda', 'Angola', '8,329,798', '8,044,735', '3.54%'],
        ['42', 'New York', 'United States', '8,323,340', '8,361,040', '-0.45%'],
        ['43', 'Ahmedabad', 'India', '8,059,441', '7,868,633', '2.42%'],
        ['44', 'Xi An Shaanxi', 'China', '8,000,965', '7,722,254', '3.61%'],
        ['45', 'Kuala Lumpur', 'Malaysia', '7,996,830', '7,780,301', '2.78%'],
        ['46', 'Hangzhou', 'China', '7,642,147', '7,437,993', '2.74%'],
        ['47', 'Hong Kong', 'China', '7,547,652', '7,490,776', '0.76%'],
        ['48', 'Dongguan', 'China', '7,407,852', '7,378,500', '0.40%'],
        ['49', 'Foshan', 'China', '7,326,852', '7,257,143', '0.96%'],
        ['50', 'Riyadh', 'Saudi Arabia', '7,231,447', '7,070,665', '2.27%'],
        ['51', 'Shenyang', 'China', '7,220,104', '7,069,012', '2.14%'],
        ['52', 'Surat', 'India', '7,184,590', '6,873,756', '4.52%'],
        ['53', 'Baghdad', 'Iraq', '7,144,260', '6,974,439', '2.43%'],
        ['54', 'Suzhou', 'China', '7,069,992', '6,703,499', '5.47%'],
        ['55', 'Santiago', 'Chile', '6,767,223', '6,723,516', '0.65%'],
        ['56', 'Dar Es Salaam', 'United Republic Of Tanzania', '6,701,650', '6,368,272', '5.23%'],
        ['57', 'Pune', 'India', '6,629,347', '6,451,618', '2.75%'],
        ['58', 'Madrid', 'Spain', '6,617,513', '6,559,041', '0.89%'],
        ['59', 'Haerbin', 'China', '6,387,195', '6,249,824', '2.20%'],
        ['60', 'Toronto', 'Canada', '6,196,731', '6,139,404', '0.93%'],
        ['61', 'Belo Horizonte', 'Brazil', '6,084,430', '6,028,319', '0.93%'],
        ['62', 'Singapore', 'Singapore', '5,935,053', '5,868,104', '1.14%'],
        ['63', 'Khartoum', 'Sudan', '5,828,858', '5,677,921', '2.66%'],
        ['64', 'Johannesburg', 'South Africa', '5,782,747', '5,635,127', '2.62%'],
        ['65', 'Qingdao', 'China', '5,619,977', '5,499,117', '2.20%'],
        ['66', 'Dalian', 'China', '5,617,849', '5,458,521', '2.92%'],
        ['67', 'Barcelona', 'Spain', '5,585,556', '5,541,127', '0.80%'],
        ['68', 'Fukuoka', 'Japan', '5,528,632', '5,540,084', '-0.21%'],
        ['69', 'Saint Petersburg', 'Russian Federation', '5,467,808', '5,426,959', '0.75%'],
        ['70', 'Ji Nan Shandong', 'China', '5,360,185', '5,205,402', '2.97%'],
        ['71', 'Yangon', 'Myanmar', '5,331,800', '5,243,989', '1.67%'],
        ['72', 'Zhengzhou', 'China', '5,322,696', '5,131,377', '3.73%'],
        ['73', 'Alexandria', 'Egypt', '5,280,664', '5,182,450', '1.90%'],
        ['74', 'Abidjan Côte', 'D\'ivoire', '5,202,762', '5,058,550', '2.85%'],
        ['75', 'Guadalajara', 'Mexico', '5,179,479', '5,100,527', '1.55%'],
        ['76', 'Ankara', 'Turkey', '5,117,603', '5,017,996', '1.98%'],
        ['77', 'Chittagong', 'Bangladesh', '5,019,824', '4,914,633', '2.14%'],
        ['78', 'Melbourne', 'Australia', '4,967,733', '4,870,388', '2.00%'],
        ['79', 'Sydney', 'Australia', '4,925,987', '4,859,432', '1.37%'],
        ['80', 'Monterrey', 'Mexico', '4,874,095', '4,792,864', '1.69%'],
        ['81', 'Addis Ababa', 'Ethiopia', '4,793,699', '4,591,983', '4.39%'],
        ['82', 'Nairobi', 'Kenya', '4,734,881', '4,556,381', '3.92%'],
        ['83', 'Hanoi', 'Viet Nam', '4,678,198', '4,479,629', '4.43%'],
        ['84', 'Brasilia', 'Brazil', '4,645,843', '4,558,991', '1.91%'],
        ['85', 'Cape Town', 'South Africa', '4,617,560', '4,524,111', '2.07%'],
        ['86', 'Jiddah', 'Saudi Arabia', '4,610,176', '4,522,216', '1.95%'],
        ['87', 'Changsha', 'China', '4,577,723', '4,460,622', '2.63%'],
        ['88', 'Kunming', 'China', '4,443,186', '4,335,924', '2.47%'],
        ['89', 'Changchun', 'China', '4,425,761', '4,332,263', '2.16%'],
        ['90', 'Xinbei', 'China', '4,398,383', '4,361,480', '0.85%'],
        ['91', 'Urumqi', 'China', '4,368,865', '4,189,926', '4.27%'],
        ['92', 'Shantou', 'China', '4,327,316', '4,249,233', '1.84%'],
        ['93', 'Rome', 'Italy', '4,257,056', '4,234,019', '0.54%'],
        ['94', 'Hefei', 'China', '4,241,514', '4,110,366', '3.19%'],
        ['95', 'Kabul', 'Afghanistan', '4,221,532', '4,114,029', '2.61%'],
        ['96', 'Montreal', 'Canada', '4,220,566', '4,195,523', '0.60%'],
        ['97', 'Tel Aviv', 'Israel', '4,181,479', '4,096,962', '2.06%'],
        ['98', 'Porto Alegre', 'Brazil', '4,137,417', '4,115,354', '0.54%'],
        ['99', 'Recife', 'Brazil', '4,127,091', '4,077,746', '1.21%'],
        ['100', 'Ningbo', 'China', '4,116,209', '3,965,588', '3.80%'],
    ]

    table = Div(SortableTable(table_data))  # FIXME: why do i need a div?

    request.client.show_html(table)
