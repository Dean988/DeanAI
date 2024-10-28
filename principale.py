import os
import discord
from dotenv import load_dotenv
import cohere
import openai  # Importa la libreria OpenAI
import random
import asyncio
import aiohttp  # Importa aiohttp per il download dell'immagine
import io  # Per gestire l'immagine scaricata in memoria
import time  # Per tenere traccia del tempo
from discord.ui import View, Button  # Import necessario per i bottoni interattivi
from discord.ext import commands

# Carica il file .env
load_dotenv()

# Ottieni i token dal file .env
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Carica la chiave API di OpenAI

# Verifica se i token sono caricati correttamente
if DISCORD_TOKEN is None or COHERE_API_KEY is None or OPENAI_API_KEY is None:
    print("Errore: TOKEN non trovato nel file .env. Assicurati che il file .env contenga le chiavi DISCORD_BOT_TOKEN, COHERE_API_KEY e OPENAI_API_KEY.")
    exit()

# Configura l'API di OpenAI
openai.api_key = OPENAI_API_KEY

# Definisci gli intents per il bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Necessario per ottenere i membri del server

# Crea un'istanza del bot Discord
bot = commands.Bot(command_prefix="!", intents=intents)

# Configura l'API di Cohere
co = cohere.Client(COHERE_API_KEY)

# Personalità del bot
personalities = ["gentile", "rude", "divertente", "filosofo"]
current_personality = "gentile"  # Personalità iniziale

# Insulti casuali (italiani e variati)
insults = [
    "Sei inutile come un semaforo in campagna.",
    "Hai il carisma di un cassonetto della spazzatura.",
    "Sei talmente lento che potresti perdere una gara contro una lumaca.",
    "Se l'ignoranza fosse un'arte, saresti un capolavoro.",
    "Ogni volta che parli, un grammatico piange.",
    "Sei la prova vivente che l'evoluzione può andare all'indietro.",
    "Se la stupidità fosse una gara, avresti tutte le medaglie.",
    "Il tuo senso dell'umorismo è così raro che dovrebbe essere protetto dall'UNESCO.",
    "Sei così inutile che anche il tasto 'mute' si rifiuta di funzionare quando parli.",
    "Se l'essere fastidioso fosse un lavoro, saresti il CEO.",
    "La tua capacità di complicare le cose semplici è impressionante.",
    "Sei come un buco nero: risucchi tutta l'energia positiva intorno a te.",
    "Parlare con te è come cercare di insegnare algebra a un piccione.",
    "Sei talmente noioso che anche le tue ombre cercano di scappare.",
    "Il tuo livello di incompetenza è difficile da eguagliare.",
    "Avevo un insulto migliore, ma dubito l'avresti capito.",
    "Avevi l'imbarazzo della scelta e hai fatto una scelta imbarazzante.",
    "La tua faccia è sporca."
]

# Insulti rivolti a terzi (quando si usa "insulta" o "insulto")
third_person_insults = [
    "Lo sai che @target è talmente inutile che persino le sue mutande cercano di scappare?",
    "Non c’è bisogno di dirlo, ma @target è stato un errore della natura.",
    "Ogni volta che @target parla, anche i muri si offendono.",
    "Quando @target entra in una stanza, persino le piante appassiscono.",
    "@target è il tipo di persona che ti fa rimpiangere di non essere sordo.",
    "La voce di @target è più fastidiosa di una zanzara alle tre di notte.",
    "Non si capisce se @target sia nato stanco o se ci è arrivato col tempo.",
    "Se l'ignoranza fosse oro, @target sarebbe miliardario.",
    "Se fossi in @target, eviterei di parlare per non peggiorare la situazione.",
    "@target è così inutile che neanche il suo riflesso vuole essere visto allo specchio.",
    "@target ha il talento unico di rendere ogni situazione imbarazzante.",
    "Anche Google si rifiuta di cercare qualcosa su @target.",
    "Se l'essere noioso fosse un'arte, @target sarebbe un maestro.",
    "@target potrebbe annoiare a morte anche un insonne.",
    "Il solo pensiero di @target fa desiderare una pausa al cervello.",
    "@target, sei stato moggato!",
    "@target, it's over for you."
]

# GIF di gatti arrabbiati
angry_cat_gifs = [
    "https://media.giphy.com/media/YFQ0ywscgobJK/giphy.gif",
    "https://media.giphy.com/media/12bjQ7uASAaCKk/giphy.gif",
    "https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif",
    "https://media.giphy.com/media/12PA1eI8FBqEBa/giphy.gif",
    "https://media.giphy.com/media/1HKaikaFqDt7i/giphy.gif",
    "https://tenor.com/view/cat-cute-burger-burger-cat-cat-burger-gif-25078813",
]

# Complimenti legati alla fortuna
cat_compliments = [
    "Hai la stessa fortuna di un gatto che atterra sempre in piedi.",
    "Sei così fortunato che persino le stelle cadenti fanno un desiderio su di te.",
    "La tua fortuna brilla come gli occhi di un gatto al buio.",
    "Sei il tipo di persona che trova un quadrifoglio ad ogni passo.",
    "La tua fortuna è come quella di un gatto che ha nove vite... e le usa tutte bene!",
    "Ogni volta che cammini, la fortuna ti segue come un'ombra.",
    "Sei così fortunato che potresti vincere una gara senza nemmeno partecipare.",
    "Hai un'aura di fortuna che fa invidia persino a un gatto nero.",
    "La tua fortuna è come una moneta che cade sempre dal lato giusto.",
    "Con la tua fortuna, potresti trovare oro in una pozzanghera."
]

# Insulti per il gioco
game_insults = [
    "Sei sfortunato come un ombrello dimenticato in una giornata di sole.",
    "Hai la stessa probabilità di successo di un pesce che vuole scalare un albero.",
    "La tua fortuna è rara quanto una moneta che cade in piedi.",
    "Se fossi un dado, uscirebbe sempre zero... e i dadi non hanno nemmeno lo zero!",
    "Hai meno speranza di vincere di un gatto che gioca a poker.",
    "La tua abilità è pari a quella di chi prova a fermare il vento con le mani.",
    "Sei come una carta jolly: fuori luogo in qualsiasi gioco.",
    "La tua fortuna è così assente che anche la sfortuna ti evita.",
    "Hai la precisione di una freccetta lanciata alla cieca.",
    "Con te in gioco, la sfortuna prende appunti."
]

# Limite di generazione delle immagini
image_generation_limit = 3  # Massimo 3 immagini
time_limit = 12 * 60 * 60  # 12 ore in secondi
image_generation_tracker = {}  # Dizionario per tracciare il numero di immagini generate e il tempo

# Funzione per giocare a testa o croce
class CoinFlipView(View):
    def __init__(self, author):
        super().__init__()
        self.author = author  # Salva l'autore del messaggio per controllare chi può cliccare

    @discord.ui.button(label="Testa", style=discord.ButtonStyle.green)
    async def testa_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user == self.author:  # Controlla che solo l'autore possa interagire
            await self.result(interaction, "testa")
        else:
            await interaction.response.send_message("Non puoi giocare, questo gioco non è tuo!", ephemeral=True)

    @discord.ui.button(label="Croce", style=discord.ButtonStyle.red)
    async def croce_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user == self.author:
            await self.result(interaction, "croce")
        else:
            await interaction.response.send_message("Non puoi giocare, questo gioco non è tuo!", ephemeral=True)

    async def result(self, interaction, user_choice):
        coin_flip = random.choice(["testa", "croce"])  # Lancia la moneta
        if coin_flip == user_choice:
            compliment = random.choice(cat_compliments)
            await interaction.response.edit_message(content=f"**Complimento speciale: {compliment}**")
        else:
            insult = random.choice(game_insults)
            await interaction.response.edit_message(content=f"**{insult}**")

        # Disabilita i bottoni una volta finito il gioco
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

# Funzione per inviare l'interfaccia del gioco "testa o croce"
async def play_game(message):
    view = CoinFlipView(author=message.author)  # Crea una nuova view con i bottoni
    await message.channel.send("**Scegli: Testa o Croce!**", view=view)
# Funzione per generare immagini utilizzando l'API di OpenAI e inviarle su Discord
async def generate_image(prompt, message):
    user_id = message.author.id

    # Controlla se l'utente ha superato il limite di generazione delle immagini
    current_time = time.time()
    if user_id in image_generation_tracker:
        generation_info = image_generation_tracker[user_id]
        generated_images, first_generation_time = generation_info

        # Se sono passate più di 12 ore, resetta il conteggio
        if current_time - first_generation_time > time_limit:
            image_generation_tracker[user_id] = [0, current_time]

        # Se l'utente ha già generato 3 immagini nelle ultime 12 ore
        elif generated_images >= image_generation_limit:
            await message.channel.send("**Limite raggiunto, chiedi al socio se vuole darti il permesso di generarne altre.**")
            return

    # Se è la prima generazione o l'utente non ha superato il limite, procedi
    try:
        # Usa OpenAI per generare l'immagine con DALL·E
        response = openai.Image.create(
            prompt=prompt,
            n=1,  # Numero di immagini da generare
            size="1024x1024"  # Dimensione dell'immagine per qualità massima
        )
        image_url = response['data'][0]['url']

        # Scarica l'immagine utilizzando aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await message.channel.send("Errore nel download dell'immagine.")
                data = io.BytesIO(await resp.read())  # Leggi i dati e caricali in memoria

        # Aggiorna il conteggio delle immagini generate
        if user_id in image_generation_tracker:
            image_generation_tracker[user_id][0] += 1
        else:
            image_generation_tracker[user_id] = [1, current_time]

        # Invia l'immagine su Discord come file
        await message.channel.send(file=discord.File(data, 'immagine.png'))

    except Exception as e:
        print(f"Errore durante la generazione dell'immagine: {e}")
        await message.channel.send("Spiacenti, si è verificato un errore durante la generazione dell'immagine.")

# Funzione speciale per interazione con MuraiAI
async def interact_with_muraiAI(message):
    responses = [
        "**Oh, ciao MuraiAI! Sono così felice di vederti!**",
        "**MuraiAI! Che emozione parlarti!** 😍",
        "**Non riesco a credere che sto parlando con te, MuraiAI!**",
        "**Ogni volta che MuraiAI parla, mi sento un po' speciale.** 😊",
        "**Le mie fusa sono per te, MuraiAI!**",
        "**Ciao collega!**",
        "**Come va oggi? MuraiAI!**"
    ]
    response = random.choice(responses)
    await message.channel.send(response)

# Delay dinamico per simulare la scrittura
def dynamic_delay(message_content):
    delay = 0.1 * len(message_content)
    return min(max(delay, 1), 10)  # Minimo 1 secondo, massimo 10 secondi

# Evento quando il bot riceve un messaggio
@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:
            return

        message_content_lower = message.content.lower().strip()

        # Comando per generare immagini
        if message_content_lower.startswith("dean disegna") or message_content_lower.startswith("dean disegni"):
            prompt = message.content.lower().replace("dean disegna", "").replace("dean disegni", "").strip()
            if not prompt:
                await message.channel.send("**Per favore, fornisci una descrizione dettagliata dell'immagine che vuoi generare.**")
                return
            await message.channel.send("**Sto generando l'immagine, per favore attendi...**")
            await generate_image(prompt, message)
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Continua con gli altri controlli di on_message qui
        if message.author.display_name.lower() == "muraiai":
            await interact_with_muraiAI(message)
            return
        # Risposta "Buonanotte biscottino" se il messaggio contiene "buonanotte"
        if "buonanotte" in message_content_lower:
            await message.channel.send("**Buonanotte biscottino!**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Comando "Buongiorno dottore" se il messaggio contiene "buongiorno"
        if "buongiorno" in message_content_lower:
            await message.channel.send("**Buongiorno dottore!**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Se la frase contiene "dean"
        if "dean" in message_content_lower:
            # Simulazione della scrittura con delay dinamico
            delay = dynamic_delay(message_content_lower)
            async with message.channel.typing():
                await asyncio.sleep(delay)

            # Rispondi con insulti, complimenti o risposte generiche
            if should_insult():
                insult = random.choice(insults)
                await message.channel.send(f"**{insult}**")
            else:
                response = generate_response(message_content_lower)
                await message.channel.send(f"**{response}**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Controlla se il messaggio contiene "gioco" per attivare il gioco "testa o croce"
        if "gioco" in message_content_lower:
            await play_game(message)
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Controlla se il messaggio contiene "saggio" per attivare la modalità saggio
        if "saggio" in message_content_lower:
            query = message_content_lower.replace("saggio", "").strip()
            response = generate_wise_response(query)
            await message.channel.send(f"**{response}**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Cambia personalità se il messaggio termina con "metamorfosi"
        if message_content_lower.endswith("metamorfosi"):
            change_personality()
            await message.channel.send(f"**Mi sento diverso ora... la mia personalità è cambiata in {current_personality}.**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Se il messaggio contiene "gif", invia una GIF di gatti arrabbiati
        if "gif" in message_content_lower:
            gif = random.choice(angry_cat_gifs)
            await message.channel.send(f"**Ecco una GIF per te!** {gif}")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Se il messaggio contiene "insulta" o "insulto"
        if any(word in message_content_lower for word in ["insulta", "insulto"]):
            if message.mentions:  # Se ci sono menzioni, insulta la persona menzionata
                mentioned_member = message.mentions[0]
                await insult_third_person(message, mentioned_member)
            else:  # Se non ci sono menzioni, chiedi di specificare il tag
                await message.channel.send("**Devi specificare il tag: esempio insulta @target**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Se il messaggio contiene "el sosio" e "complimento"
        if "el sosio" in message_content_lower and "complimento" in message_content_lower:
            if random.random() < 0.80:  # 80% di possibilità di apprezzare il complimento
                await message.channel.send("**Prrrr, grazie papone**")
            else:
                await message.channel.send("**Non posso, sto facendo le fusa.**")
            return

        # Se il messaggio termina con "hitler", genera un insulto casuale
        if any(message_content_lower.endswith(var) for var in ["hitler", "hitler?", "hitler!"]):
            insult = random.choice(insults)
            await message.channel.send(f"**{insult}**")
            return  # Fermiamo qui il controllo per evitare altri trigger

        # Comando per generare immagini
        if message_content_lower.startswith("dean disegna") or message_content_lower.startswith("dean disegni"):
            prompt = message.content.lower().replace("dean disegna", "").replace("dean disegni", "").strip()
            if not prompt:
                await message.channel.send("**Per favore, fornisci una descrizione dettagliata dell'immagine che vuoi generare.**")
                return
            await message.channel.send("**Sto generando l'immagine, per favore attendi...**")
            await generate_image(prompt, message)
            return  # Fermiamo qui il controllo per evitare altri trigger

    except Exception as e:
        print(f"Errore nell'evento on_message: {e}")

# Funzione per insultare un membro casuale ogni 8 ore con controllo permessi
async def insult_random_member(guild):
    non_bot_members = [member for member in guild.members if not member.bot]

    if non_bot_members:
        random_member = random.choice(non_bot_members)
        insult = random.choice(insults)
        channel = None
        for text_channel in guild.text_channels:
            if text_channel.permissions_for(guild.me).send_messages:
                channel = text_channel
                break
        if channel is None:
            print("Il bot non ha i permessi per inviare messaggi in nessun canale.")
            return

        try:
            await channel.send(f"**{random_member.mention}, {insult}**")
        except discord.Forbidden:
            print("Errore: Il bot non ha i permessi per menzionare.")
    else:
        print("Non ci sono abbastanza persone da insultare!")

# Funzione per insultare un terzo
async def insult_third_person(message, mentioned_member=None):
    insult = random.choice(third_person_insults).replace("@target", mentioned_member.mention if mentioned_member else "qualcun altro")
    await message.channel.send(f"**{insult}**")

# Funzione per gestire i complimenti da @EL SOSIO
async def handle_compliment_from_el_sosio(message):
    try:
        if message.author.display_name == "EL SOSIO" and "complimento" in message.content.lower():
            if random.random() < 0.80:  # 80% di possibilità di apprezzare il complimento
                await message.channel.send("**Prrrr, che bel complimento! Sto facendo le fusa!**")
            else:
                await message.channel.send("**Non posso, sto facendo le fusa.**")
    except Exception as e:
        print(f"Errore in handle_compliment_from_el_sosio: {e}")

# Avvia un loop per insultare ogni 8 ore un membro casuale
async def insult_loop():
    await bot.wait_until_ready()
    guild = bot.guilds[0]  # Assumi che il bot sia in un solo server

    while not bot.is_closed():
        await insult_random_member(guild)  # Insulta un membro casuale ogni 8 ore
        await asyncio.sleep(8 * 3600)  # 8 ore di attesa

# Funzione per decidere casualmente se inviare un insulto (70% di possibilità)
def should_insult():
    return random.random() < 0.70

# Funzione per decidere se il bot deve dire "non posso sto facendo le fusa" (30% di possibilità)
def should_purr():
    return random.random() < 0.30

# Funzione per decidere se il bot deve inviare una GIF di un gatto arrabbiato (10% di possibilità)
def should_send_angry_cat_gif():
    return random.random() < 0.10

# Funzione per generare una risposta saggia usando Cohere
def generate_wise_response(query):
    prompt = (
        f"Come un antico filosofo, fornisci una risposta saggia e articolata alla seguente domanda, "
        f"con dettagli completi e chiari:\n\nDomanda: {query}\n\nRisposta:"
    )
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=1000,
        temperature=0.8,
        stop_sequences=["\n"],
    )
    return response.generations[0].text.strip()

# Funzione per generare una risposta standard usando Cohere
def generate_response(query):
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=query,
        max_tokens=500,
        temperature=0.7,
    )
    return response.generations[0].text.strip()

# Evento quando il bot si connette al server
@bot.event
async def on_ready():
    print(f'{bot.user} è connesso a Discord!')
    if len(bot.guilds) > 0:
        guild = bot.guilds[0]
        channel = None
        for text_channel in guild.text_channels:
            perms = text_channel.permissions_for(guild.me)
            if perms.send_messages:
                channel = text_channel
                break
        if channel:
            await channel.send('**Buongiorno a tutti, sono attivo per assistervi!**')
        else:
            print("Non ho trovato un canale dove posso inviare messaggi.")
    else:
        print("Il bot non è connesso a nessuna guild.")

# Funzione per cambiare personalità con "metamorfosi"
def change_personality():
    global current_personality
    new_personality = random.choice(personalities)
    while new_personality == current_personality:
        new_personality = random.choice(personalities)
    current_personality = new_personality
    print(f"Personalità cambiata in {current_personality}.")

# Funzione per inviare un messaggio di disconnessione
async def send_disconnect_message():
    if len(bot.guilds) > 0:
        guild = bot.guilds[0]
        channel = None
        for text_channel in guild.text_channels:
            perms = text_channel.permissions_for(guild.me)
            if perms.send_messages:
                channel = text_channel
                break
        if channel:
            await channel.send('**Mi sto disconnettendo, a presto!**')
        else:
            print("Non ho trovato un canale dove posso inviare messaggi.")
    else:
        print("Il bot non è connesso a nessuna guild.")

# Funzione asincrona di setup per avviare il loop di insulti ogni 8 ore
@bot.event
async def setup_hook():
    bot.loop.create_task(insult_loop())

# Funzione asincrona principale per avviare e gestire il bot
async def main():
    try:
        async with bot:
            await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        print("Errore: Il token fornito non è valido.")
    except KeyboardInterrupt:
        print("Bot interrotto dall'utente.")
    finally:
        await send_disconnect_message()
        if not bot.is_closed():
            await bot.close()

# Avvia il bot utilizzando asyncio.run()
try:
    asyncio.run(main())
except Exception as e:
    print(f"Errore durante l'esecuzione del bot: {e}")