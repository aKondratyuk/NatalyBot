from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, \
    PasswordField, IntegerField, FloatField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, InputRequired, EqualTo, NumberRange

# Нужно решить, хранить ли "---"
language_list = ['', '---', 'English', 'Afrikaans', 'Arabic', 'Belorussian', 'Bulgarian', 'Burmese', 'Cantonese',
                 'Croatian',
                 'Czech', 'Danish', 'Dutch', 'Esperanto', 'Estonian', 'Finnish', 'French', 'German', 'Greek', 'Gujrati',
                 'Hebrew', 'Hindi', 'Hungarian', 'Icelandic', 'Indian', 'Indonesian', 'Italian', 'Japanese', 'Korean',
                 'Latvian', 'Lithuanian', 'Malay', 'Mandarin', 'Marathi', 'Moldovian', 'Nepalese', 'Norwegian',
                 'Persian', 'Polish', 'Portuguese', 'Punjabi', 'Romanian', 'Russian', 'Serbian', 'Spanish', 'Swedish',
                 'Tagalog', 'Taiwanese', 'Tamil', 'Telugu', 'Thai', 'Tongan', 'Turkish', 'Ukrainian', 'Urdu',
                 'Vietnamese', 'Visayan']
# Нужно решить, хранить ли "---"
language_level = ['', 'Very bad', 'Basic', 'Intermediate', 'Good', 'Fluent']
martial_status_list = ['I prefer not to say', 'Single', 'Attached', 'Divorced', 'Widow']
religion_list = ['I prefer not to say', 'Adventist', 'Agnostic', 'Atheist', 'Baptist', 'Buddhist', 'Caodaism',
                 'Catholic', 'Christian', 'Hindu', 'Iskcon', 'Jainism', 'Jewish', 'Methodist', 'Mormon', 'Moslem',
                 'Orthodox', 'Pentecostal', 'Protestant', 'Quaker', 'Scientology', 'Shinto', 'Sikhism', 'Spiritual',
                 'Taoism', 'Wiccan', 'Zoroastrian', 'Other']
ethnicity_list = ['I prefer not to say', 'African', 'African American', 'Asian', 'Caucasian', 'East Indian', 'Hispanic',
                  'Indian', 'Latino', 'Mediterranean', 'Middle Eastern', 'Mixed']
countries_list = ['American Samoa', 'Andorra', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia',
                  'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Barbados', 'Belarus', 'Belgium',
                  'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia/Herzegowina', 'Botswana', 'Bouvet Island',
                  'Brazil', 'British Ind. Ocean', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Cameroon', 'Canada',
                  'Cape Verde', 'Cayman Islands', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocoa (Keeling) Is.',
                  'Colombia', 'Comoros', 'Costa Rica', 'Cote Divoire', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic',
                  'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador',
                  'Equatorial Guinea', 'Estonia', 'Falkland Islands', 'Faroe Islands', 'Fiji', 'Finland', 'France',
                  'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada',
                  'Guadeloupe', 'Guam', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Honduras', 'Hong Kong',
                  'Hungary', 'Iceland', 'India', 'Iran', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan',
                  'Kazakhstan', 'Kenya', 'Kiribati', 'Korea', 'Kuwait', 'Kyrgyzstan', 'Latvia', 'Lebanon', 'Lesotho',
                  'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macau', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia',
                  'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte',
                  'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique',
                  'Namibia', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Niue',
                  'Norfolk Island', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama', 'Papua New Guinea', 'Paraguay',
                  'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Reunion', 'Romania',
                  'Russia', 'Saint Lucia', 'Samoa', 'San Marino', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles',
                  'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'Spain',
                  'Sri Lanka', 'St. Helena', 'Swaziland', 'Sweden', 'Switzerland', 'Taiwan', 'Tajikistan', 'Tanzania',
                  'Thailand', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
                  'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'USA', 'Uruguay',
                  'Uzbekistan', 'Vanuatu', 'Vatican', 'Venezuela', 'Viet Nam', 'Virgin Islands', 'Western Sahara',
                  'Zambia', 'Yemen']
children_list = ['without children', 'with children', '1 child', '2 children', '3 children', '4 children', '5 children',
                 '6 children']
where_children_list = ['I will tell you later', 'living with me', 'not living with me', 'sometimes living with me']
want_children_list = ['I will tell you later', 'No', 'Yes', 'Maybe', "Doesn't matter"]
height_list = ['I prefer not to say', '4\'7" (140cm) or below', '4\'8" - 4\'9" (141-145cm)',
               '4\'10" - 4\'11" (146-150cm)', '5\'0" - 5\'1"  (151-155cm)', '5\'2" - 5\'3"  (156-160cm)',
               '5\'4" - 5\'5"  (161-165cm)', '5\'6" - 5\'7"  (166-170cm)', '5\'8" - 5\'9" (171-175cm)',
               '5\'10" - 5\'11" (176-180cm)', '6\'0" - 6\'1"  (181-185cm)', '6\'2" - 6\'3"  (186-190cm)',
               '6\'4" (191cm) or above']
body_type_list = ['I prefer not to say', 'Average', 'Ample', 'Athletic', 'Attractive', 'Slim', 'Very Cuddly']
education_list = ['I prefer not to say', 'High School graduate', 'Higher Education', 'College student',
                  'AA (2 years college)', 'BA/BS (4 years college)', 'Some grad school', 'Grad school student',
                  'MA/MS/MBA', 'PhD/Post doctorate', 'JD']
income_list = ['I prefer not to say', '$10,000/year and less', '$10,000-$30,000/year', '$30,000-$50,000/year',
               '$50,000-$70,000/year', '$70,000/year and more']
smoker_list = ['I prefer not to say', 'No', 'Rarely', 'Often', 'Very often']
drinker_list = ['I prefer not to say', 'No', 'Rarely', 'Often', 'Very often']
looking_for_a_height_list = ['I prefer not to say', '4\'7" (140cm) or below', '4\'8" - 4\'9" (141-145cm)',
                             '4\'10" - 4\'11" (146-150cm)', '5\'0" - 5\'1"  (151-155cm)', '5\'2" - 5\'3"  (156-160cm)',
                             '5\'4" - 5\'5"  (161-165cm)', '5\'6" - 5\'7"  (166-170cm)', '5\'8" - 5\'9" (171-175cm)',
                             '5\'10" - 5\'11" (176-180cm)', '6\'0" - 6\'1"  (181-185cm)', '6\'2" - 6\'3"  (186-190cm)',
                             '6\'4" (191cm) or above']
looking_for_a_body_type_list = ['I prefer not to say', 'Average', 'Ample', 'Athletic', 'Attractive', 'Slim',
                                'Very Cuddly']
relationship_list = ['Activity Partner', 'Friendship', 'Marriage', 'Relationship', 'Romance', 'Casual',
                     'Travel Partner', 'Pen Pal']
zodiacs_list = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn',
                'Aquarius', 'Pisces']


# site login form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField()


# create site user form
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password', [InputRequired()])
    admin = BooleanField("Admin")
    submit = SubmitField()


# profiles create form
class AddProfileForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = StringField('Пароль', [DataRequired()])
    invite_name = StringField("Имя инвайта", validators=[DataRequired()])
    msg_limit = BooleanField("Достигнут лимит сообщений")
    submit = SubmitField()


# excel file upload form
class UploadProfilesForm(FlaskForm):
    file = FileField("Загрузить excel файл",
                     validators=[FileRequired(), FileAllowed(['xls', 'xlsx'], 'Excel Document only!')])
    sheet_number = IntegerField("Номер листа", validators=[DataRequired()])
    submit = SubmitField()


# form for creation of profiles detailed description
class AddProfileDescriptionForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    age = IntegerField('Age', validators=[NumberRange(min=18, max=100, message='Age can be from 18 to 100!')])
    body_type = SelectField("Body type", choices=body_type_list)
    children = SelectField("Children", choices=children_list)
    city = StringField("City")
    country = SelectField("Country", choices=countries_list)
    credits_to_open_letter = FloatField('Credits to open letter', default=0)
    description = StringField("Description")
    drinker = SelectField("Drinker", choices=drinker_list)
    education = SelectField("Education", choices=education_list)
    ethnicity = SelectField("Ethnicity", choices=ethnicity_list)
    height = SelectField("Height", choices=height_list)
    ideal_match_description = StringField("Ideal match description")
    income = StringField("Income")
    language_1 = SelectField('Language 1', choices=language_list)
    language_2 = SelectField('Language 2', choices=language_list)
    language_3 = SelectField('Language 3', choices=language_list)
    last_online = StringField("Last online")
    looking_for_a_body_type = SelectField("Looking for a body type", choices=looking_for_a_body_type_list)
    looking_for_a_height = SelectField("Looking for a height", choices=looking_for_a_height_list)
    looking_for_an_age_range = StringField("Looking for an age range")
    marital_status = SelectField("Marital status", choices=martial_status_list)
    name = StringField("Name")
    nickname = StringField("Nickname")
    occupation = StringField("Occupation")
    rate = FloatField("Rate", default=0)
    relationship = SelectMultipleField("Relationship", choices=[(i, i) for i in relationship_list])
    religion = SelectField("Religion", choices=religion_list)
    sex = StringField('Sex')
    smoker = SelectField("Smoker", choices=smoker_list)
    votes = IntegerField("Votes", default=0)
    want_children = SelectField("Want children", choices=want_children_list)
    zodiac = SelectField("Zodiac", choices=zodiacs_list)
    submit = SubmitField()
