"""Plexos model enums that define the data schema."""

from enum import Enum, StrEnum
from typing import Optional, cast


class Schema(Enum):
    """Enum that defines the Plexos Schema."""

    Attributes = ("t_attribute", "attribute_id")
    AttributeData = ("t_attribute_data", "attribute_id")
    Class = ("t_class", "class_id")
    ClassGroup = ("t_class_group", "class_group_id")
    Objects = ("t_object", "object_id")
    Categories = ("t_category", "category_id")
    Collection = ("t_collection", "collection_id")
    CollectionReport = ("t_collection_report", None)
    Memberships = ("t_membership", "membership_id")
    Property = ("t_property", "property_id")
    PropertyGroup = ("t_property_group", "property_group_id")
    PropertyReport = ("t_property_report", None)
    PropertyTag = ("t_property_tag", None)
    Data = ("t_data", "data_id")
    Band = ("t_band", "band_id")
    Report = ("t_report", None)
    DateFrom = ("t_date_from", None)
    DateTo = ("t_date_to", None)
    MemoData = ("t_memo_data", None)
    Message = ("t_message", None)
    Action = ("t_action", None)
    Config = ("t_config", None)
    Tags = ("t_tag", "tag_id")
    Text = ("t_text", "text_id")
    Units = ("t_unit", "unit_id")

    @property
    def name(self) -> str:
        """Table name associated with this schema element.

        Returns
        -------
        str
            The underlying table name parsed from the enum value.
        """
        return cast(str, self.value[0])

    @property
    def label(self) -> str | None:
        """Primary label column name for the schema element, if any.

        Returns
        -------
        str | None
            The label column used as a default identifier when available.
        """
        return cast(str | None, self.value[1])


class ClassEnum(StrEnum):
    """Enum that defines the different Plexos classes."""

    System = "System"
    Generator = "Generator"
    PowerStation = "PowerStation"
    Fuel = "Fuel"
    FuelContract = "FuelContract"
    Power2X = "Power2X"
    Battery = "Battery"
    Storage = "Storage"
    Waterway = "Waterway"
    Emission = "Emission"
    Abatement = "Abatement"
    PhysicalContract = "PhysicalContract"
    Reserve = "Reserve"
    Reliability = "Reliability"
    FinancialContract = "FinancialContract"
    Cournot = "Cournot"
    RSI = "RSI"
    Region = "Region"
    Pool = "Pool"
    Zone = "Zone"
    Node = "Node"
    Load = "Load"
    Line = "Line"
    MLF = "MLF"
    Transformer = "Transformer"
    FlowControl = "FlowControl"
    Interface = "Interface"
    Contingency = "Contingency"
    Hub = "Hub"
    TransmissionRight = "TransmissionRight"
    HeatPlant = "HeatPlant"
    HeatNode = "HeatNode"
    HeatStorage = "HeatStorage"
    GasField = "GasField"
    GasPlant = "GasPlant"
    GasPipeline = "GasPipeline"
    GasNode = "GasNode"
    GasStorage = "GasStorage"
    GasDemand = "GasDemand"
    GasDSMProgram = "GasDSMProgram"
    GasBasin = "GasBasin"
    GasZone = "GasZone"
    GasContract = "GasContract"
    GasTransport = "GasTransport"
    GasPath = "GasPath"
    GasCapacityReleaseOffer = "GasCapacityReleaseOffer"
    WaterPlant = "WaterPlant"
    WaterPipeline = "WaterPipeline"
    WaterNode = "WaterNode"
    WaterStorage = "WaterStorage"
    WaterDemand = "WaterDemand"
    WaterZone = "WaterZone"
    WaterPumpStation = "WaterPumpStation"
    WaterPump = "WaterPump"
    Vehicle = "Vehicle"
    ChargingStation = "ChargingStation"
    Fleet = "Fleet"
    Company = "Company"
    Commodity = "Commodity"
    Process = "Process"
    Facility = "Facility"
    Maintenance = "Maintenance"
    FlowNetwork = "FlowNetwork"
    FlowNode = "FlowNode"
    FlowPath = "FlowPath"
    FlowStorage = "FlowStorage"
    Entity = "Entity"
    Market = "Market"
    DataFile = "DataFile"
    Variable = "Variable"
    Timeslice = "Timeslice"
    Global = "Global"
    Scenario = "Scenario"
    WeatherStation = "WeatherStation"
    Model = "Model"
    Project = "Project"
    Horizon = "Horizon"
    Report = "Report"
    Stochastic = "Stochastic"
    Preview = "Preview"
    LTPlan = "LTPlan"
    PASA = "PASA"
    MTSchedule = "MTSchedule"
    STSchedule = "STSchedule"
    Transmission = "Transmission"
    Production = "Production"
    Competition = "Competition"
    Performance = "Performance"
    Diagnostic = "Diagnostic"
    List = "List"
    Layout = "Layout"
    Constraint = "Constraint"
    Objective = "Objective"
    DecisionVariable = "DecisionVariable"
    NonlinearConstraint = "NonlinearConstraint"
    Purchaser = "Purchaser"

    @classmethod
    def _missing_(cls, value: object) -> Optional["ClassEnum"]:
        """Resolve class values that differ only by whitespace."""
        if not isinstance(value, str):
            return None

        normalized = value.replace(" ", "")
        for member in cls:
            if member.value.replace(" ", "") == normalized:
                return member

        return None


class CollectionEnum(StrEnum):
    """Enum that defines the different Plexos colections via Collection Name."""

    Generators = "Generators"
    Fuels = "Fuels"
    HeadStorage = "HeadStorage"
    TailStorage = "TailStorage"
    Nodes = "Nodes"
    Storages = "Storages"
    Emissions = "Emissions"
    Reserves = "Reserves"
    Batteries = "Batteries"
    Regions = "Regions"
    Zones = "Zones"
    Region = "Region"
    Zone = "Zone"
    Lines = "Lines"
    NodeFrom = "NodeFrom"
    NodeTo = "NodeTo"
    Transformers = "Transformers"
    Interfaces = "Interfaces"
    Models = "Models"
    Scenario = "Scenario"
    Scenarios = "Scenarios"
    Horizon = "Horizon"
    Horizons = "Horizons"
    Report = "Report"
    Reports = "Reports"
    ReferenceNode = "ReferenceNode"
    PASA = "PASA"
    MTSchedule = "MTSchedule"
    STSchedule = "STSchedule"
    Transmission = "Transmission"
    Production = "Production"
    Diagnostic = "Diagnostic"
    Diagnostics = "Diagnostics"
    Performance = "Performance"
    DataFiles = "DataFiles"
    Constraint = "Constraint"
    Constraints = "Constraints"
    Variables = "Variables"
    Purchasers = "Purchasers"
    PowerStations = "PowerStations"
    FuelContracts = "FuelContracts"
    Power2X = "Power2X"
    Waterways = "Waterways"
    Abatements = "Abatements"
    PhysicalContracts = "PhysicalContracts"
    Reliability = "Reliability"
    FinancialContracts = "FinancialContracts"
    Cournots = "Cournots"
    RSIs = "RSIs"
    Pools = "Pools"
    Loads = "Loads"
    MLFs = "MLFs"
    FlowControls = "FlowControls"
    Contingencies = "Contingencies"
    Hubs = "Hubs"
    TransmissionRights = "TransmissionRights"
    HeatPlants = "HeatPlants"
    HeatNodes = "HeatNodes"
    HeatStorages = "HeatStorages"
    GasFields = "GasFields"
    GasPlants = "GasPlants"
    GasPipelines = "GasPipelines"
    GasNodes = "GasNodes"
    GasStorages = "GasStorages"
    GasDemands = "GasDemands"
    GasDSMPrograms = "GasDSMPrograms"
    GasBasins = "GasBasins"
    GasZones = "GasZones"
    GasContracts = "GasContracts"
    GasTransports = "GasTransports"
    GasPaths = "GasPaths"
    GasCapacityReleaseOffers = "GasCapacityReleaseOffers"
    WaterPlants = "WaterPlants"
    WaterPipelines = "WaterPipelines"
    WaterNodes = "WaterNodes"
    WaterStorages = "WaterStorages"
    WaterDemands = "WaterDemands"
    WaterZones = "WaterZones"
    WaterPumpStations = "WaterPumpStations"
    WaterPumps = "WaterPumps"
    Vehicles = "Vehicles"
    ChargingStations = "ChargingStations"
    Fleets = "Fleets"
    Companies = "Companies"
    Commodities = "Commodities"
    Processes = "Processes"
    Facilities = "Facilities"
    Maintenances = "Maintenances"
    FlowNetworks = "FlowNetworks"
    FlowNodes = "FlowNodes"
    FlowPaths = "FlowPaths"
    FlowStorages = "FlowStorages"
    Entities = "Entities"
    Markets = "Markets"
    Objectives = "Objectives"
    DecisionVariables = "DecisionVariables"
    NonlinearConstraints = "NonlinearConstraints"
    Timeslices = "Timeslices"
    Globals = "Globals"
    WeatherStations = "WeatherStations"
    Projects = "Projects"
    Stochastic = "Stochastic"
    Preview = "Preview"
    LTPlan = "LTPlan"
    Competition = "Competition"
    Lists = "Lists"
    Layouts = "Layouts"


PLEXOS_CLASS_COUNT_V9_V10 = 96
PLEXOS_COLLECTION_COUNT_V92 = 776
PLEXOS_COLLECTION_COUNT_V10 = 806


def str2enum(string: str, schema_enum: type[Enum] = Schema) -> Schema | None:
    """Convert string to enum."""
    for e in schema_enum:
        if e.name == string:
            return cast(Schema, e)
    return None


def get_default_collection(class_enum: ClassEnum) -> CollectionEnum:
    """Return default collection for class."""
    # Special cases for Data File and Battery objects
    special_cases = {
        ClassEnum.DataFile: CollectionEnum.DataFiles,
        ClassEnum.Battery: CollectionEnum.Batteries,
    }

    if class_enum in special_cases:
        return special_cases[class_enum]

    normalized_key = class_enum.value.replace(" ", "")

    # Handle consonant+y plurals used by several classes (e.g., Facility -> Facilities).
    plural_ies = (
        f"{normalized_key[:-1]}ies"
        if (
            normalized_key.endswith("y")
            and len(normalized_key) > 1
            and normalized_key[-2].lower() not in "aeiou"
        )
        else None
    )
    plural_es = f"{normalized_key}es" if normalized_key.endswith(("s", "x", "z", "ch", "sh")) else None

    candidates = (
        f"{normalized_key}s",
        plural_es,
        plural_ies,
        normalized_key,
        f"{class_enum.name}s",
        class_enum.name,
    )

    for candidate in candidates:
        if candidate and candidate in CollectionEnum.__members__:
            return CollectionEnum[candidate]

    raise KeyError(f"Default collection is not defined for class {class_enum.value!r}")


def _parse_str_enum(enum_cls: type[Enum], value: str | Enum) -> Enum:
    """Parse a string or Enum to an Enum instance of the specified enum class."""
    if isinstance(value, enum_cls):
        return value

    # Exact value match
    for e in enum_cls:
        if e.value == value:
            return e

    # Enum name without spaces
    if isinstance(value, str):
        key = value.replace(" ", "")
        try:
            return enum_cls[key]
        except KeyError:
            raise ValueError(f"{value!r} is not a valid {enum_cls.__name__}")
    else:
        raise ValueError(f"{value!r} is not a valid {enum_cls.__name__}")


def parse_class_enum(value: str | ClassEnum) -> ClassEnum:
    """Parse a string or ClassEnum to a ClassEnum instance."""
    return cast(ClassEnum, _parse_str_enum(ClassEnum, value))


def parse_collection_enum(value: str | CollectionEnum) -> CollectionEnum:
    """Parse a string or CollectionEnum to a CollectionEnum instance."""
    return cast(CollectionEnum, _parse_str_enum(CollectionEnum, value))
