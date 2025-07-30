import gradio as gr
import asyncio
import os
from agents import Agent, Runner
from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool

load_dotenv()
# 🔐 Load API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 🧠 Memory setup
store = InMemoryStore(index={"dims": 1536, "embed": "openai:text-embedding-3-small"})
manage_memory = create_manage_memory_tool(namespace=("employee", "user"))
search_memory = create_search_memory_tool(namespace=("employee", "user"))

# ☕ Coffee Agents
coffee_agent = Agent(
    name="Coffee Agent",
    instructions="""
Assist with coffee-related tasks:
- Suggest drinks
- Place coffee orders
- Track loyalty points
""",
    tools=[
        Agent(name="Coffee Recommender", instructions="Suggest coffee based on preferences.").as_tool("recommend_coffee", "Recommend the right coffee."),
        Agent(name="Coffee Orderer", instructions="Place coffee orders with local vendors.").as_tool("place_order", "Place the coffee order."),
        Agent(name="Loyalty Tracker", instructions="Retrieve loyalty points from the system.").as_tool("track_loyalty", "Check loyalty balance.")
    ]
)

# 🍱 Food Agent
food_agent = Agent(
    name="Food Agent",
    instructions="Assist with food ordering, lunch suggestions, and canteen info.",
    tools=[
        Agent(name="Lunch Suggester", instructions="Suggest meals from preferred cuisines.").as_tool("suggest_lunch", "Suggest lunch options."),
        Agent(name="Meal Preorder", instructions="Place lunch orders.").as_tool("preorder_meal", "Preorder lunch."),
        Agent(name="Canteen Status", instructions="Report current canteen queues and specials.").as_tool("canteen_status", "Check canteen availability.")
    ]
)

# 🏋️ Gym Agent
gym_agent = Agent(
    name="Gym Agent",
    instructions="Support employees with gym bookings, workouts, and attendance tracking.",
    tools=[
        Agent(name="Slot Booker", instructions="Book gym timeslots.").as_tool("book_gym_slot", "Book gym time."),
        Agent(name="Workout Coach", instructions="Suggest workouts.").as_tool("workout_ideas", "Recommend fitness routines."),
        Agent(name="Attendance Tracker", instructions="Track gym attendance history.").as_tool("track_visits", "View visit history.")
    ]
)

# 🧑‍💼 HR Agent
hr_agent = Agent(
    name="HR Agent",
    instructions="Manage HR services such as leave, policies, and expense claims.",
    tools=[
        Agent(name="Leave Applier", instructions="Submit leave forms.").as_tool("apply_leave", "Apply for leave."),
        Agent(name="Balance Checker", instructions="Check leave balance.").as_tool("check_leave_balance", "Check available leave."),
        Agent(name="Policy Reader", instructions="Summarize HR policies.").as_tool("get_policy", "Get HR policy details."),
        Agent(name="Expense Submitter", instructions="Help file expense claims.").as_tool("submit_expense", "Submit an expense claim.")
    ]
)

# 📚 Learning Agent
learning_agent = Agent(
    name="Learning Agent",
    instructions="Assist with courses, progress, and mentorship suggestions.",
    tools=[
        Agent(name="Course Picker", instructions="Suggest learning paths and courses.").as_tool("recommend_course", "Propose learning options."),
        Agent(name="Progress Tracker", instructions="Track L&D module completions.").as_tool("track_learning", "Show course progress."),
        Agent(name="Mentor Matcher", instructions="Recommend internal mentors.").as_tool("suggest_mentors", "Connect to a relevant mentor.")
    ]
)

# 🚗 Transport Agent
transport_agent = Agent(
    name="Transport Agent",
    instructions="Handle commute suggestions, parking, shuttle booking, and weather-based transport help.",
    tools=[
        Agent(name="Commute Planner", instructions="Suggest commuting options.").as_tool("commute_options", "Find commuting options."),
        Agent(name="Parking Booker", instructions="Book parking spots.").as_tool("book_parking", "Reserve a parking lot."),
        Agent(name="Shuttle Scheduler", instructions="Request shuttle transport.").as_tool("request_shuttle", "Schedule shuttle ride."),
        Agent(name="Weather Adjuster", instructions="Suggest options based on rain or heat.").as_tool("weather_adjustment", "Adapt transport to weather.")
    ]
)

# 🧑‍💻 IT Pit Stop Agent
it_pit_stop_agent = Agent(
    name="IT Pit Stop Agent",
    instructions="Support laptop/software-related issues, appointment booking, and queue alerts.",
    tools=[
        Agent(name="IT Appointment Scheduler", instructions="Book IT service slots.").as_tool("book_it_support", "Book IT support appointment."),
        Agent(name="Queue Alert System", instructions="Notify employees 15, 10, and 5 minutes before their queue number.").as_tool("preempt_queue_alert", "Preemptively alert user before their turn.")
    ]
)

# 🏥 Medical Clinic Agent
medical_clinic_agent = Agent(
    name="Medical Clinic Agent",
    instructions="Manage medical appointment bookings and time-based queue notifications.",
    tools=[
        Agent(name="Clinic Slot Booker", instructions="Book appointments with doctors.").as_tool("book_medical_appointment", "Book medical appointment."),
        Agent(name="Queue Notification Service", instructions="Notify 15, 10, and 5 minutes before appointment.").as_tool("preempt_medical_queue", "Notify before medical queue.")
    ]
)

# 🎡 Recreation Club Agent
recreation_club_agent = Agent(
    name="Recreation Club Agent",
    instructions="""
Assist with facility bookings and provide info on corporate leisure offers:
- Book party venues or club rooms.
- Share corporate deals for Singapore Zoo, River Safari, Gardens by the Bay, and Science Museum.
- Track membership and redeem reward points.
""",
    tools=[
        Agent(name="Facility Booker", instructions="Book or check availability for party/event venues.").as_tool("book_venue", "Book a party venue or club facility."),
        Agent(name="Corporate Offers Explorer", instructions="List current discounts for local attractions.").as_tool("list_offers", "Explore corporate deals."),
        Agent(name="Offer Details Retriever", instructions="Get full offer details for a selected place.").as_tool("get_offer_details", "More info on selected offer."),
        Agent(name="Membership Checker", instructions="Check club membership or point balance.").as_tool("check_membership_status", "Check club membership."),
        Agent(name="Points Redeemer", instructions="Redeem reward points for eligible benefits.").as_tool("redeem_points", "Use reward points.")
    ]
)

# 💳 Payment Agent
payment_agent = Agent(
    name="Payment Agent",
    instructions="""
Manage payments for food and coffee orders using the Dash account system.
- Show available menu items and prices
- Enable selection of items for purchase
- Process payments and return confirmation
- Check Dash account balance and transaction history
""",
    tools=[
        Agent(name="Menu Viewer", instructions="Fetch menu items for food and coffee with prices.").as_tool("get_menu", "View available food and coffee items."),
        Agent(name="Item Payment Processor", instructions="Select and pay for one or more items from the menu.").as_tool("pay_for_items", "Make a payment for selected items."),
        Agent(name="Dash Balance Checker", instructions="Show Dash account balance and recent transactions.").as_tool("dash_summary", "View Dash account status.")
    ]
)


# 🧠 Coordinator Agent (copied from user code)
employee_assistant = Agent(
    name="Employee Assistant",
    instructions="""
You're the central assistant for all employee needs.
Use appropriate tools to handle:
- Coffee needs
- Food & canteen
- Gym routines
- HR services
- Learning & development
- Transport & commute
- IT support appointments & alerts
- Medical appointments & alerts
- Recreation & corporate offers
- Payments for food and beverages

Also use memory tools for personalized support.
""",
    tools=[
        coffee_agent.as_tool("coffee_assist", "Assist with coffee recommendations, orders, and rewards."),
        food_agent.as_tool("food_assist", "Help with lunch choices and food court info."),
        gym_agent.as_tool("gym_assist", "Manage workouts and gym access."),
        hr_agent.as_tool("hr_assist", "Handle HR requests and policies."),
        learning_agent.as_tool("learning_assist", "Support training, learning, and mentoring."),
        transport_agent.as_tool("transport_assist", "Plan employee transport and commute."),
        it_pit_stop_agent.as_tool("it_support_assist", "Manage IT appointments and notify ahead of time."),
        medical_clinic_agent.as_tool("clinic_assist", "Book medical appointments and notify before appointments."),
        recreation_club_agent.as_tool("recreation_assist", "Book venues or explore leisure benefits."),
        payment_agent.as_tool("payment_assist", "Pay for food and coffee with your Dash account."),
    ]
)

# ⚙️ Async executor for the agent
async def employee__assistant(topic):
    result = await Runner.run(employee_assistant, topic)
    return result.final_output

# 💬 Wrapper to use in Gradio
def chatbot_interface(user_input):
    return asyncio.run(employee__assistant(user_input))

# 🚀 Launch Gradio using Interface
iface = gr.Interface(
    fn=run_employee_chat,
    inputs=gr.Textbox(lines=2, label="🧑‍💼 Ask your Employee Assistant"),
    outputs=gr.Textbox(lines=15, label="🤖 Response"),
    title="Employee Assistant Chatbot 🤖",
    description="Ask about ☕ coffee, 🍱 food, 🧘 gym, 🧑‍💼 HR, 📚 learning, 🛺 transport, 🛠️ IT, 🏥 medical, 🎉 recreation, 💳 payment.",
)