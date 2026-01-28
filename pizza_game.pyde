import random
import time
add_library('minim')
res_height = 800
res_length = 1400
button_w = 400
button_h = 200
toppings = []
baking_time = "normal"
game_started= True

sound = None
station_page = None
pack_page = None
start_screen = None

pepperoni_img = None
olives_img = None

#colors
RED     = color(141, 35, 35)
PINK    = color(249, 186, 186)
YELLOW  = color(235, 182, 23)
REMOVE  = color(112, 112, 112)
GREEN = color(99,107,47)
DARKRED = color(178,20,20)
WHITE   = color(255)


class Button:
    def __init__(self, x, y, w, h, text, col):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.col = col
    
    def draw(self):
        fill(self.col)
        rect(self.x, self.y, self.w, self.h, 30)
        fill(WHITE)
        textAlign(CENTER, CENTER)
        textSize(30)
        text(self.text, self.x + self.w/2, self.y + self.h/2)
    
    def is_clicked(self):
        return (self.x <= mouseX <= self.x+self.w and self.y <= mouseY <= self.y+self.h)


#colleciton of all the buttons used in the gamr
all_buttons = {
    'cheese': Button(99.8,144.5,116.2,180,"",YELLOW),
    'sauce': Button(275.9,144.5,116.2,180,"",RED),
    'open shop': Button((res_length-button_w)/2,(res_height-button_h-100), button_w,button_h-100,"Open Shop",RED),
    'dough spread okay': Button(558.7,341.2,280.9,55.7,"Okay!",PINK),
    'submit oven': Button(997.7,611.9,280.9,55.7,"Submit To Oven",RED),
    'package': Button(488.5,483.4,422.9,141.7,"Package Pizza",RED),
    'submit': Button(514,636.7,371.9,97.8,"Submit Pizza",RED),
    'pepperoni': Button(1009, 144, 116, 180, "", DARKRED),
    'olives': Button(1184, 144, 116, 180, "", GREEN),
    'next day': Button((res_length - button_w)/2, 600, button_w, 120, "Next Day", RED),
    'restart': Button((res_length - button_w)/2, 600, button_w, 120, "Restart Game", RED),
    'shop': Button((res_length - button_w)/2, 500, button_w, 120, "Go to Shop", RED),
    "buy_pepperoni": Button(300, 250, 300, 100, "Buy Pepperoni ($50)", RED),
    "buy_olives": Button(800, 250, 300, 100, "Buy Olives ($50)", GREEN),
    "buy_oven": Button(490, 450, 400, 100, "Buy Deluxe Oven ($120)", DARKRED),
    "start_day" : Button(550, 550, 300, 120, "Start Day", RED),
    
}



#these are used for the orders
cheese_bool = {
               True: "Cheese",
               False: "No Cheese"
               }
sauce_bool = {
              True: "Sauce",
              False: "No Sauce",
              }
oven_time = {
             "normal": 6,
             "deluxe": 3,
             }

item_prices = {
               "pepperoni": 50,
               "olives": 50
               }
ingredient_cost = {
                   "dough": 2,
                   "sauce":1,
                   "cheese": 1,
                   "pepperoni": 3,
                   "olives": 3
                   }


class Dough:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    def draw(self):
        fill(247,239,210)
        ellipse(self.x, self.y, self.w, self.h)
    
    
    def is_clicked(self):
        #checks the distance to make sure that its within the dough boundaries
        return dist(mouseX, mouseY, self.x, self.y) <= self.w/2


class Message:
    def __init__(self, note):
        self.note = note
        self.visible = True
        self.button = Button(560, 360, 250, 60, "Okay!", PINK)

    def display(self):
        if not self.visible:
            return

        fill(RED)
        rect(480, 180, 440, 260, 20)

        fill(WHITE)
        textAlign(CENTER, CENTER)
        textSize(28)
        text(self.note, 480 + 220, 180 + 120)

        self.button.draw()

    def pressed(self):
        if not self.visible:
            return False
        if self.button.is_clicked():
            self.visible = False
            return True
        return False


class Order:
    def __init__(self, cheese, sauce, topping):
        self.dough = True
        self.cheese = cheese
        self.sauce = sauce
        self.topping = topping

    def match(self, other): #compares two orders
        return (self.cheese == other.cheese and
                self.sauce == other.sauce and
                self.topping == other.topping)
    def display(self, number):
        fill(0)
        textSize(32)
        textAlign(LEFT, TOP)

        text("ORDER: " + sauce_bool[self.sauce] + ", " + cheese_bool[self.cheese] + ", " + self.topping, 40,30) #displays the order in the top left


class Station:
    def __init__(self):
        self.dough_added = False
        self.sauce_added = False
        self.cheese_added = False
    

        self.dough_size = 0
        self.sauce_size = 0
        self.cheese_size = 0

        self.dough_max = 408
        self.sauce_max = 360
        self.cheese_max = 330
        
        
        self.topping = None
        self.message = None
        
    def add_topping(self,topping):
        if not self.dough_added:
            self.message = Message("Add dough first!")
            return
        if self.topping is not None:
            self.message = Message("Topping already added!")
            return
        if game.inventory[topping] <= 0:
            self.message = Message("You don't own this topping!")
            return
        self.topping = topping
        game.inventory[topping] -=1
        game.current_day.total_ingredient_cost += ingredient_cost[topping]
        
    def add_dough(self):
        if self.dough_added:
            self.message = Message("Already Added!")
        else:
            self.dough_added = True
            game.current_day.total_ingredient_cost += ingredient_cost["dough"]

    def add_cheese(self):
        if not self.dough_added:
            self.message = Message("Add Dough First!")
        elif self.cheese_added:
            self.message = Message("Already Added!")
        else:
            self.cheese_added = True
            game.current_day.total_ingredient_cost += ingredient_cost["cheese"]

    def add_sauce(self):
        if not self.dough_added:
            self.message = Message("Add Dough First!")
        elif self.sauce_added:
            self.message = Message("Already Added!")
        else:
            self.sauce_added = True
            game.current_day.total_ingredient_cost += ingredient_cost["sauce"]
            
    #animates the circles
    def animate(self):
        if self.dough_added and self.dough_size < self.dough_max:
            self.dough_size += 20
        if self.sauce_added and self.sauce_size < self.sauce_max:
            self.sauce_size += 20
        if self.cheese_added and self.cheese_size < self.cheese_max:
            self.cheese_size += 20
    def submit_pizza(self):
        return Order(self.cheese_added,self.sauce_added,self.topping or "No Toppings")
    def reset(self):
        self.dough_added = False
        self.sauce_added = False
        self.sauce_size = 0
        self.cheese_added = False
        self.dough_size = 0
        self.cheese_size = 0
        self.message = None
        self.topping = None




def display_station(st): #st is the station class
    image(station_page, 0, 0, res_length, res_height)
    all_buttons["sauce"].draw()
    all_buttons["cheese"].draw()
    all_buttons["pepperoni"].draw()
    all_buttons["olives"].draw()
    all_buttons["submit oven"].draw()
    
    #these are the final sizes after animation
    if st.dough_added:
        fill(247, 239, 210)
        ellipse(res_length/2, res_height/2, st.dough_size, st.dough_size)

    if st.sauce_added:
        fill(200, 30, 30)
        ellipse(res_length/2, res_height/2, st.sauce_size, st.sauce_size)

    if st.cheese_added:
        fill(235, 182, 23)
        ellipse(res_length/2, res_height/2, st.cheese_size, st.cheese_size)
    
    if st.topping == "pepperoni":
        global pepperoni_img
        image(pepperoni_img, res_length/2 - 120, res_height/2 - 120, 240, 240)
    if st.topping == "olives":
        image(olives_img, res_length/2 - 120, res_height/2 - 120, 240, 240)








def mousePressed():
    global game_started, station

    #game over function
    if game.game_over:
        if all_buttons["restart"].is_clicked():
            game.reset_game()
        return

    # this starts the game
    if game_started:
        if all_buttons["open shop"].is_clicked():
            game_started = False
        return

    # initiates the summary of the day 
    if game.current_day.day_finished== True and  game.show_shop == False:
        if all_buttons["shop"].is_clicked():
            game.show_shop = True
            return
        return

    # adds function to the shop
    if game.show_shop:

        if all_buttons["buy_pepperoni"].is_clicked():
            if game.money >= 50:
                game.money -= 50
                game.inventory["pepperoni"] += 1
        if all_buttons["buy_olives"].is_clicked():
            if game.money >= 50:
                game.money -= 50
                game.inventory["olives"] += 1

        if all_buttons["buy_oven"].is_clicked():
            if game.money >= 120 and not game.oven_deluxe:
                game.money -= 120
                game.oven_deluxe = True

        if all_buttons["start_day"].is_clicked():
            game.show_shop = False
            game.start_new_day()

        return   # <-- IMPORTANT: Prevent gameplay clicks

    # tracks the clicks on the dough grid
    for d in game.current_day.dough_grid:
        if d.is_clicked():
            if not station.dough_added:
                game.current_day.dough_grid.remove(d)
            station.add_dough()
            return

    if station.message and station.message.visible== True:
        if station.message.pressed():
            station.message = None
        return

    # adds cheese sauce toppings everything
    if all_buttons["cheese"].is_clicked():
        station.add_cheese()
        return

    if all_buttons["sauce"].is_clicked():
        station.add_sauce()
        return
    if all_buttons["pepperoni"].is_clicked():
        station.add_topping("pepperoni")
        return

    if all_buttons["olives"].is_clicked():
        station.add_topping("olives")
        return
    
    #from the oven into packaging
    
    if oven.pizza_ready==True and all_buttons["package"].is_clicked():
        game.start_packing()
        oven.active = False
        oven.pizza_ready = False
        return

    #subitting after packaging
    if game.pack_active == True and game.pack_done == True:
        if all_buttons["submit"].is_clicked():
            pizza_made = station.submit_pizza()
            correct = pizza_made.match(
                game.current_day.orders[game.current_day.current_order]
            )

            game.current_day.submitted_orders.append(pizza_made)
            game.current_day.scores.append(correct)
            BASE_PRICE = 15
            topping_bonus = {
                "No Toppings": 0,
                "pepperoni": 5,
                "olives": 5
            }

            if correct== True:
                bonus = topping_bonus.get(pizza_made.topping, 0)
                revenue = BASE_PRICE + bonus
                game.money += revenue
                game.current_day.total_revenue += revenue

            # Reset
            game.pack_active = False
            game.pack_done = False
            station.reset()
            game.current_day.next_order()
        return

    #bake pizza
    if all_buttons["submit oven"].is_clicked():
        if not station.dough_added:
            station.message = Message("Add dough first!")
        else:
            oven.start()
            
            
            
            
            
            
            
            
            
class Oven:
    def __init__(self):
        self.active = False #active while there is a pizza being backed
        self.pizza_ready = False #true when the pizza is finished from the oven
        self.start_time = 0
        self.target = 6 #initial speed of oven
    def start(self):
        self.active = True
        self.start_time = millis() #initiates a timer
        self.pizza_ready = False
    def update(self):
        if game.oven_deluxe == True:
            self.target = oven_time["deluxe"]
        else:
            self.target = oven_time["normal"]
        if self.active == True:
            time = (millis() - self.start_time) / 1000
            if time >= self.target:
                self.pizza_ready = True
    def display(self):
        background(50)

        fill(255)
        textAlign(CENTER, CENTER)

        if self.pizza_ready==False:
            textSize(60)
            remaining = int(self.target - (millis() - self.start_time)/1000)
            text("Baking... " + str(max(0, remaining)), res_length/2, res_height/2)
        else:
            textSize(60)
            text("Pizza Ready!", res_length/2, res_height/2 - 60)
            all_buttons["package"].draw()
            
station = Station()

oven = Oven()











class Game:
    def __init__(self, station, oven):
        self.station = station
        self.oven = oven
        self.money = 100
        self.rating = 2.5
        self.game_over = False
        self.win = False
        self.show_shop = False
        self.oven_deluxe = False 
        self.inventory = {
                          "pepperoni": 0, #inventory can be increased through the item shop
                          "olives": 0
                          }
        self.current_day = Day(self)
        self.rating_updated = False

        
        
        #variables associated with the packaging and its animations
        self.pack_active = False
        self.pack_x = 0
        self.pack_speed = 25
        self.pack_done = False
    def update(self):
        if self.current_day.day_finished:
            self.oven.active = False
            self.oven.pizza_ready = False
            self.pack_active = False
            self.pack_done = False
            self.pack_x = 0
            return
        self.current_day.update()
        if self.pack_active == True:
            self.update_packing()
            return
        if self.oven.active == True:
            self.oven.update()
            return
        
        self.station.animate()
        
    def available_toppings(self):
        unlocked = ["No Toppings"]
        if self.inventory["pepperoni"]>0:
            unlocked.append("pepperoni")
        if self.inventory["olives"]>0:
            unlocked.append("olives")
        return unlocked
    def display(self):
        if self.show_shop:
            self.display_shop()
            return
        if self.game_over:
            self.display_end_screen()
            return
        if self.current_day.day_finished:
            self.display_day_summary()
            return
    

        if self.pack_active:
            self.animate_pack()
            return
    
        if self.oven.active:
            self.oven.display()
            return

        display_station(self.station)
        
        #the top right labels (money, rating and the time left in the day)
    
        fill(RED)
        rect(750, 25, 200, 50)
        fill(255)
        textSize(28)
        textAlign(CENTER, CENTER)
        text("$" + str(self.money), 750, 25, 200, 50)
    
        fill(RED)
        rect(950, 25, 200, 50)
        fill(255)
        text("Rating: " + str(self.rating), 950, 25, 200, 50)

        fill(RED)
        rect(1150, 25, 200, 50)
        fill(255)
        text("Time: " + str(int(self.current_day.time_left())), 1150, 25, 200, 50)
        self.current_day.get_current_order().display(self.current_day.current_order)

    
    
    
        for d in self.current_day.dough_grid:
            d.draw()
        if self.station.message:
            self.station.message.display()
    def display_end_screen(self):
        background(0)
        fill(255)
        textAlign(CENTER, CENTER)

        textSize(60)
        if self.win:
            text("Congrats, you won!", res_length/2, 250)
        else:
            text("You lost.", res_length/2, 250)

        textSize(30)
        text("Click restart to play again.", res_length/2, 350)

        all_buttons["restart"].draw()
    def start_packing(self):
        #restarting everything (m)
        self.pack_active = True
        self.pack_done = False
        self.pack_x = 0
    def update_packing(self):
        image(pack_page,0,0,res_length,res_height)
        if self.pack_active ==True:
            if self.pack_x <700:
                self.pack_x +=self.pack_speed
            else:
                self.pack_done = True
    def animate_pack(self):
        if self.pack_active == True:
            fill(247,239,210)
            ellipse(self.pack_x, res_height/2, 360, 360)


            if self.station.sauce_added:
                fill(200, 30, 30)
                ellipse(self.pack_x, res_height/2, 330, 330)
            if self.station.cheese_added:
                fill(235, 182, 23)
                ellipse(self.pack_x, res_height/2, 310, 310)
                
            if self.station.topping == "pepperoni":
                image(pepperoni_img, self.pack_x - 120, res_height/2 - 120, 240, 240)

            if self.station.topping == "olives":
                image(olives_img, self.pack_x - 120, res_height/2 - 120, 240, 240)

            if self.pack_done:
                all_buttons["submit"].draw()
    def display_day_summary(self):
        background(0)
        fill(255)
        textAlign(CENTER, CENTER)

        score = self.current_day.final_score()
        revenue = self.current_day.total_revenue
        cost = self.current_day.total_ingredient_cost
        profit = self.current_day.profit()
        change = self.current_day.rating_change()
    
        textSize(50)
        text("DAY COMPLETED", res_length/2, 150)
        textSize(30)
        text("Correct Pizzas: " + str(score) + "/9", res_length/2, 250)
        text("Revenue: " + str(revenue), res_length/2, 300)
        text("Ingredient Cost: " + str(cost), res_length/2, 350)
        text("Net Profit: " + str(profit), res_length/2, 400)
        if not self.rating_updated:
            self.rating += change
            self.rating_updated = True
            if self.rating >= 5:
                self.game_over = True
                self.win = True
            elif self.rating <= 1:
                self.game_over = True
                self.win = False
    
        if self.game_over == False:
            all_buttons["shop"].draw()
    def start_new_day(self):
        #resets all the edited variables when called because its a new day so everything starts new
        self.current_day = Day(self)
        self.station.reset()
        self.oven.active = False
        self.oven.pizza_ready = False
        self.pack_active = False
        self.pack_done = False
        self.pack_x = 0
        self.rating_updated = False
    def reset_game(self):
        #reset variables that carry on throughout the days like money,rating...
        self.money = 100
        self.rating = 3.0
        self.inventory = {"pepperoni": 0, "olives": 0}
        self.station.reset()
    
        self.oven.active = False
        self.oven.pizza_ready = False
    
        self.pack_active = False
        self.pack_done = False
        self.pack_x = 0
    
        self.current_day = Day(self)
        self.game_over = False
        self.win = False
        self.rating_updated = False

        global game_started
        game_started = True
    def display_shop(self):
        background(30)
        fill(255)
        textAlign(CENTER, CENTER)
        textSize(50)
        text("ITEM SHOP", res_length/2, 100)
        textSize(28)
        text("Money: $" + str(self.money), res_length/2, 170)
        all_buttons["buy_pepperoni"].draw()
        all_buttons["buy_olives"].draw()
        all_buttons["start_day"].draw()
        textSize(24)
        text("Pepperoni: " + str(self.inventory['pepperoni']), res_length/2, 330)
        text("Olives: " + str(self.inventory['olives']), res_length/2, 370)
        if self.oven_deluxe == True:
            text("Oven: Deluxe", res_length/2, 410)
        
        else:
            text("Oven: Normal", res_length/2, 410)
            all_buttons["buy_oven"].draw()
            
        
    






class Day:
    max_orders = 9 #since there is only 9 dough spots, only 9 orders are mad per day MAX
    day_time_limit = 60
    def __init__(self,game):
        self.game = game
        self.orders = []
        self.total_ingredient_cost = 0
        self.generate_next_order()
        self.dough_grid = []
        self.total_revenue = 0
        self.stock_dough()
        self.current_order = 0
        self.submitted_orders = []
        self.day_finished = False
        self.scores = []
        self.start_time = millis() 
        self.time_up = False
    def profit(self):
        return self.total_revenue - self.total_ingredient_cost
    def rating_change(self):
        score = self.final_score()
        if score >= 7:
            return 0.5
        elif score >= 5:
            return 0
        else:
            return -0.5
    def time_left(self):
        passed = (millis() - self.start_time)/1000

        return max(0, Day.day_time_limit - passed)
    def get_current_order(self):
        return self.orders[self.current_order]
    def final_score(self):
        score=0
        for i in self.scores:
            if i == True:
                score+=1
        return score
    def generate_next_order(self):
        #after an order is completed, this function is called to generate the next order 
        topping = random.choice(self.game.available_toppings())
        order = Order(
        random.choice([True, False]),
        random.choice([True, False]),
        topping
        )
        self.orders.append(order)
    def next_order(self):
        
        if self.time_left() <= 0:
            print("OVERRR")
            self.day_finished = True
            return
        if len(self.orders) < Day.max_orders:
            self.generate_next_order()

        if self.current_order < Day.max_orders - 1:
            self.current_order += 1
        else:
            self.day_finished = True
    def update(self):
        if self.time_left() <= 0:
            self.day_finished = True
    def stock_dough(self):
        self.dough_grid = []
        start_x = 165
        start_y = 407
        spacing = 80
    
        for row in range(3):
            for col in range(3):
                x = start_x + col * spacing
                y = start_y + row * spacing
                self.dough_grid.append(Dough(x, y, 61,61))
                
                
game = Game(station,oven)











 


def setup():
    global station_page,pack_page,pepperoni_img,olives_img,start_screen,sound
    size(res_length, res_height)
    
    #all the pages and toppings
    station_page = loadImage("station.png")
    pack_page = loadImage("package.png")
    pepperoni_img = loadImage("pepperoni.png")
    start_screen = loadImage("starter.png")
    olives_img = loadImage("olives.png")
    
    #sound
    minim = Minim(this)
    sound = minim.loadFile("pizzeria.mp3")
    sound.loop()
    sound.setGain(-5)  # optional: lower volume (0 = loud)
def draw():
    global game_started

    if game_started == True:
        image(start_screen, 0, 0, res_length, res_height)
        all_buttons["open shop"].draw()
        return
    game.update()
    game.display()
