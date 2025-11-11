from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Float, Enum, ForeignKey, Integer, Date
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

# --- Bloque en el que se define las "opciones predefinidas" para los campos enum --- #
class Gender(enum.Enum):
    masculine = "masculine"         # No se puede usar boolean con otra cosa que no sean valores lógicos true o false 
    femenine = "femenine"           # Para añadir una lista de "opciones predefinidas" es necesario usar Enum (enumeración)

class Classification(enum.Enum):
    mammal = "mammal"
    artificial = "artificial"
    sentient = "sentient"
    gastropod = "gastropod"
    reptile = "reptile"
    amphibian = "amphibian"
    insectoid = "insectoid"
    unknown = "unknown"

class Designation(enum.Enum):
    sentient = "sentient"
    non_sentient = "non-sentient"
    semi_sentient = "semi-sentient"
    unknown = "unknown"
# ----------------------------------------------------------------------------------- #


# AÑADIR FAVORITOS DEL USUARIO #
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Characters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    species_id: Mapped[int] = mapped_column(ForeignKey("species.id"))
    weight: Mapped[float] = mapped_column(Float)
    hair_color: Mapped[str] = mapped_column(String(20))
    eye_color: Mapped[str] = mapped_column(String(20))
    birth_year: Mapped[str] = mapped_column(String(10))
    homeworld_id: Mapped[int] = mapped_column(ForeignKey("planets.id"))

    # --- Relaciones --- #
    homeworld: Mapped["Planets"] = relationship("Planets", back_populates="residents") 
    species: Mapped["Species"] = relationship("Species", back_populates="residents")
    films: Mapped[list["Films"]] = relationship(secondary="characters_films",back_populates="characters")
    starships: Mapped[list["Starships"]] = relationship(secondary="characters_starships", back_populates="pilots")
    vehicles: Mapped[list["Vehicles"]] = relationship(secondary="characters_vehicles", back_populates="pilots")
    # ------------------ #


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender.value,
            "weight": self.weight,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "homeworld": self.homeworld.name if self.homeworld else None,
            "films": [film.title for film in self.films],
        }
    
class Films(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(40))
    episode_id: Mapped[int] = mapped_column(Integer)
    director: Mapped[str] = mapped_column(String(20))
    producer: Mapped[str] = mapped_column(String(40))
    release_date: Mapped[str] = mapped_column(Date)
    opening_crawl: Mapped[str] = mapped_column(String(250))
   
    # --- Relaciones --- #
    characters: Mapped[list["Characters"]] = relationship(secondary="characters_films", back_populates="films")
    starships: Mapped[list["Starships"]] = relationship(secondary="starships_films", back_populates="films")
    vehicles: Mapped[list["Vehicles"]] = relationship(secondary="vehicles_films", back_populates="films")
    # ------------------ #

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "episode_id": self.episode_id,
            "director": self.director,
            "producer": self.producer,
            "release_date": self.release_date,
            "opening_crawl": self.opening_crawl,
            "characters": [char.name for char in self.characters]
        }

class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40))
    climate: Mapped[str] = mapped_column(String(40))
    terrain: Mapped[str] = mapped_column(String(40))
    population: Mapped[int] = mapped_column(Integer)

    # --- Relaciones --- #
    residents: Mapped[list["Characters"]] = relationship("Characters", back_populates="homeworld")
    species: Mapped[list["Species"]] = relationship("Species", back_populates="homeworld")
    # ------------------ #

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

class Species(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    classification: Mapped[Classification] = mapped_column(Enum(Classification), nullable=False)
    designation: Mapped[Designation] = mapped_column(Enum(Designation), nullable=False)
    average_height: Mapped[float] = mapped_column(Float)
    skin_colors: Mapped[str] = mapped_column(String(100))
    hair_colors: Mapped[str] = mapped_column(String(100))
    eye_colors: Mapped[str] = mapped_column(String(100))
    average_lifespan_in_years: Mapped[str] = mapped_column(String(20))
    language: Mapped[str] = mapped_column(String(50))
    homeworld_id: Mapped[int] = mapped_column(ForeignKey("planets.id")) # RELACIÓN 1 A 1 

    # --- Relaciones --- #
    residents: Mapped[list["Characters"]] = relationship("Characters", back_populates="species")
    homeworld: Mapped["Planets"] = relationship("Planets", back_populates="species")
    # ------------------ #

    def serialize(self):
        return {
        "id": self.id,
        "name": self.name,
        "classification": self.classification,
        "designation": self.designation,
        "average_height": self.average_height,
        "skin_colors": self.skin_colors,
        "hair_colors": self.hair_colors,
        "eye_colors": self.eye_colors,
        "average_lifespan_in_years": self.average_lifespan_in_years,
        "language": self.language,
        "homeworld_id": self.homeworld_id,
        }

class Starships(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(20))
    manufacturer: Mapped[str] = mapped_column(String(40))
    cost_in_credits: Mapped[int] = mapped_column(Integer)
    length: Mapped[int] = mapped_column(Integer)
    max_atmosphering_speed: Mapped[int] = mapped_column(Integer)
    crew: Mapped[str] = mapped_column(String(20))
    passengers: Mapped[int] = mapped_column(Integer)
    cargo_capacity: Mapped[int] = mapped_column(Integer)
    consumables: Mapped[str] = mapped_column(String(20))
    hyperdrive_rating: Mapped[str] = mapped_column(String(20))
    MGLT: Mapped[str] = mapped_column(String(20))
    starship_class: Mapped[str] = mapped_column(String(20))

    # --- Relaciones --- #
    pilots: Mapped[list["Characters"]] = relationship(secondary="characters_starships", back_populates="starships")
    films: Mapped[list["Films"]] = relationship(secondary="starships_films", back_populates="starships")
    # ------------------ #

    def serialize(self):
            return {
                "id": self.id,
                "name": self.name,
                "model": self.model,
                "manufacturer": self.manufacturer,
                "cost_in_credits": self.cost_in_credits,
                "length": self.length,
                "max_atmosphering_speed": self.max_atmosphering_speed,
                "crew": self.crew,
                "passengers": self.passengers,
                "cargo_capacity": self.cargo_capacity,
                "consumables": self.consumables,
                "hyperdrive_rating": self.hyperdrive_rating,
                "MGLT": self.MGLT,
                "starship_class": self.starship_class,
                "pilots": [pil.name for pil in self.pilots]
            }

class Vehicles(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(20))
    manufacturer: Mapped[str] = mapped_column(String(40))
    length: Mapped[int] = mapped_column(Integer)
    max_atmosphering_speed: Mapped[int] = mapped_column(Integer)
    crew: Mapped[str] = mapped_column(String(20))
    passengers: Mapped[int] = mapped_column(Integer)
    cargo_capacity: Mapped[int] = mapped_column(Integer)
    consumables: Mapped[str] = mapped_column(String(20))
    vehicle_class: Mapped[str] = mapped_column(String(20))

    # --- Relaciones --- #
    pilots: Mapped[list["Characters"]] = relationship(secondary="characters_vehicles",back_populates="vehicles")
    films: Mapped[list["Films"]] = relationship(secondary="vehicles_films", back_populates="vehicles")
    # ------------------ #

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "length": self.length,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "crew": self.crew,
            "passengers": self.passengers,
            "cargo_capacity": self.cargo_capacity,
            "consumables": self.consumables,
            "vehicle_class": self.vehicle_class,
            "pilots": [pil.name for pil in self.pilots]
        }

    

# ------------------- Tablas de intermedias ------------------- #
class CharacterFilm(db.Model):
    __tablename__ = "characters_films"
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), primary_key=True)
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"), primary_key=True)

class CharacterStarship(db.Model):
    __tablename__ = "characters_starships"
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), primary_key=True)
    starship_id: Mapped[int] = mapped_column(ForeignKey("starships.id"), primary_key=True)

class CharacterVehicle(db.Model):
    __tablename__ = "characters_vehicles"
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"), primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), primary_key=True)

class StarshipFilm(db.Model):
    __tablename__ = "starships_films"
    starship_id: Mapped[int] = mapped_column(ForeignKey("starships.id"), primary_key=True)
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"), primary_key=True)

class VehicleFilm(db.Model):
    __tablename__ = "vehicles_films"
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), primary_key=True)
    film_id: Mapped[int] = mapped_column(ForeignKey("films.id"), primary_key=True)
# ------------------------------------------------------------ #