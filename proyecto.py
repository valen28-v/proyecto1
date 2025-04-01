import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Constante de Coulomb
K = 8.9875517873681764 * 10**9  

def registrar_instancias(cls): #registra todas las instancias de la clase
    cls.instancias = []  # crea la lista para almacenar las instancias
    original_init = cls.__init__

    def nuevo_init(self, *args, **kwargs): #Define un nuevo constructor para registrar las instancias
        original_init(self, *args, **kwargs)  # Llama al constructor original
        cls.instancias.append(self) # Añade la instancia actual a la lista de instancias
    
    cls.__init__ = nuevo_init  # Reemplaza el constructor original con uno nuevo
    return cls    # Devuelve la clase modificada

def medir_tiempo(cls):   # Decorador para medir tiempo de inicialización
    original_init = cls.__init__      # Guarda el constructor original
    
    def nuevo_init(self, *args, **kwargs):       # Define un nuevo constructor con mensajes de tiempo
        print(f"Inicializando {cls.__name__}...")     # Dice que comenzo la inicialización
        original_init(self, *args, **kwargs)
        print(f"{cls.__name__} inicializado correctamente.")
    
    cls.__init__ = nuevo_init   # Reemplaza el constructor original
    return cls   # Devuelve la clase modificada

@registrar_instancias    # Aplica el decorador registrar_instancias a la clase EntidadFisica
class EntidadFisica:       # Constructor de la clase
    def __init__(self, x, y): #esta cosa define la cordenada x e y para la entidad fisica. coloca las tildes, me dio pereza
        self.x = x
        self.y = y

class Carga(EntidadFisica):   # esta clase hereda de EntidadFisica 
    def __init__(self, valor, x, y): # Constructor de la clase Carga
        super().__init__(x, y)    # Llama al constructor de la clase padre (EntidadFisica) para establecer las coordenadas x e y
        self.valor = valor  # Asigna el valor de la carga eléctrica 

    def calcular_campo(self, X, Y):      # Método para calcular el campo eléctrico generado por las cargas
        K = 8.99e9  # Constante de Coulomb (N·m²/C²)
        dx = [[x - self.x for x in fila] for fila in X]   # Calcula las diferencias en x entre cada punto de la malla (X) y la posición de la cargas
        dy = [[y - self.y for y in fila] for fila in Y]   # Calcula las diferencias en y entre cada punto de la malla (Y) y la posición de la cargas
        r = [[math.sqrt(dx[i][j]**2 + dy[i][j]**2) for j in range(len(dx[0]))] for i in range(len(dx))]     # Calcula la distancia (r) desde la carga a cada punto de la malla
        
        for i in range(len(r)):
            for j in range(len(r[0])):
                if r[i][j] == 0:
                    r[i][j] = 1e-10  # Evitar división por cero 
        
        return [[K * self.valor / r[i][j]**2 for j in range(len(r[0]))] for i in range(len(r))]     # Calcula el campo eléctrico en cada punto

class SistemaDeCargas:
    def __init__(self):   
        self.cargas = []   # Inicializa una lista vacía para almacenar las cargas del sistema
    
    def agregar_carga(self, carga):   
        self.cargas.append(carga)   # Añade la carga a la lista de cargas del sistema
    
    def calcular_campos(self, X, Y):    # Método para calcular los campos eléctricos generados por todas las cargas
        E_magnitudes = [[0 for _ in range(len(X[0]))] for _ in range(len(X))]    # Inicializa matriz para almacenar magnitudes de campo de cargas positivas
        mE_magnitudes = [[0 for _ in range(len(X[0]))] for _ in range(len(X))]     # Inicializa matriz para almacenar magnitudes de campo de cargas negativas
        
        for carga in self.cargas:   # esto itera sobre todas las cargas del sistema
            E = carga.calcular_campo(X, Y)    # Calcula el campo eléctrico generado por esta carga en todos los puntos
            if carga.valor > 0:
                for i in range(len(E)):
                    for j in range(len(E[0])):
                        E_magnitudes[i][j] += E[i][j]     # Suma su contribución a la matriz de campos positivos
            else:
                for i in range(len(E)):
                    for j in range(len(E[0])):
                        mE_magnitudes[i][j] += E[i][j]    # Suma su contribución a la matriz de campos negativos
        
        return E_magnitudes, mE_magnitudes   # Retorna ambas matrices (campos positivos y negativos por separado)

@medir_tiempo
class SimuladorCampoElectrico:
    def __init__(self, x_min, x_max, y_min, y_max, resolucion):      # igual que antes esto es el constructor del simulador
        self.x_min, self.x_max = x_min, x_max     # Límites del área de simulación en el eje X
        self.y_min, self.y_max = y_min, y_max     # Límites del área de simulación en el eje Y
        self.resolucion = resolucion   # número de puntos en cada dimensión
        self.paso = (x_max - x_min) / (resolucion - 1)     # Calcula el tamaño del paso entre puntos de la malla
        self.sistema = SistemaDeCargas()   # Crea un sistema de cargas vacío
        self.X, self.Y = self.crear_malla()      # Genera las matrices de coordenadas X, Y para la malla
    
    def crear_malla(self):
        x_vals = [self.x_min + i * self.paso for i in range(self.resolucion)]
        y_vals = [self.y_min + i * self.paso for i in range(self.resolucion)]
        X = [[x for x in x_vals] for _ in y_vals]
        Y = [[y for _ in x_vals] for y in y_vals]
        return X, Y
    
    def agregar_carga(self, carga):       # Método para agregar una carga al sistema
        self.sistema.agregar_carga(carga)    # Cada vez que este método se ejecuta, se almacena una nueva carga en el sistema.
     
    def ejecutar_simulacion(self):      # Calcula los campos eléctricos para todas las cargas
        E_magnitudes, mE_magnitudes = self.sistema.calcular_campos(self.X, self.Y)     # Retorna las magnitudes de los campos positivos y negativos
        
        fig = plt.figure(figsize=(8, 6))     #grafica 3d. 
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(self.X, self.Y, np.array(E_magnitudes), cmap='Reds', alpha=0.8)
        ax.plot_surface(self.X, self.Y, np.array(mE_magnitudes), cmap='Blues', alpha=0.8)
        
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Campo Eléctrico (N/C)")
        ax.set_title("Mapa 3D del Campo Eléctrico")
        
        plt.show()
# Programa principal
if __name__ == "__main__":
    n = int(input("Ingrese la cantidad de cargas: "))
    simulador = SimuladorCampoElectrico(-4, 4, -4, 4, 500)
    
    for i in range(n):
        q = float(input(f"Ingrese el valor de la carga {i+1} (en Coulombs): "))
        x = float(input(f"Ingrese la coordenada x de la carga {i+1} (en metros): "))
        y = float(input(f"Ingrese la coordenada y de la carga {i+1} (en metros): "))
        simulador.agregar_carga(Carga(q, x, y))
    
    simulador.ejecutar_simulacion()