
import numpy as np
from scipy.integrate import odeint
import pandas as pd
from pandas import ExcelWriter

''' Se construye un DataFrame a partir de la tabla paramétrica de municipios:
    Nombre de la localidad / municipio / provincia / pais,

    Población de la localidad / municipio / provincia / pais,

    Infectados en día cero,

    Coeficiente beta (ratio de contagio, tal que 1/beta mide la probabilidad de que un susceptible se infecte cuando
    entra en contacto con un infectado),

    Coeficiente gamma (ratio de recuperación, 1/gamma es la cantidad de días que se tarda en promedio la recuperación),

    Coeficiente sigma de incubación (ratio de incubación, 1/sigma es el tiempo promedio de incubación)

    R0 (índice de reproducción del virus, es la relación beta/gamma, se estima en 2.25, representa el número de
    nuevos infectados producidos por un infectado si toda la población es susceptible)'''

df1 = pd.read_excel('Localidades SEIR.xlsx')

# Armamos un dataframe vacío donde pondremos todos los resultados
data = pd.DataFrame()

# Se arman listas con los vectores que componen el DataFrame
nom = df1.Localidad
ini = df1.Inicial
gam = df1.Gamma
sig = df1.Sigma
bet = df1.Beta
pob = df1.Poblacion

# Definimos la cantidad de días de la ventana de proyección
dias = 180

# Se construyen un elemento a partir de una función zip para iterar los 5 parámetros juntos en un bucle
zipped = zip(pob, ini, gam, bet, nom, sig)

# Se arma la iteración para proyectar la curva de cada municipio con sus propios parámetros
for a,b,c,d,e,f in zipped:

    # Pobliación del municipio a partir del elemento "a" de zipped (pob).
    N = a

    # Número inicial de contagios en el momento cero a partir del elemento "b" de zipped (ini)
    # Suponemos que el elemento Rec de recuperado en el primer día es 0.
    # Suponemos que los expuestos en el primer día es el producto de contagios y el índice de reproducción (R0 o beta/gamma)
    I0, Rec0, E0 = b, d/c, 0

    # Por diferencia calculamos la población Posible que es la diferencia entre la total, la expuesta, la contagiada y la recuperada.
    S0 = N - E0 - I0 - Rec0

    # Ratio de contagio (beta), ratio de recuperación promedio (gamma) y ratio de incubación (sigma).
    beta, gamma, sigma = d, c, f # la división de beta sobre gamma da el coeficiente r0 (se estima en 2.25)

    # Armamos un vector temporal para proyectar 180 días, con frecuencia diaria
    t = np.linspace(0, dias, dias, dtype = "int")

    # Se crea una función para resolver el modelo SIR de ecuaciones diferenciales
    # Para más detalle ver https://belenus.unirioja.es/~jvarona/coronavirus/SEIR-coronavirus.pdf
    def deriv(y, t, N, beta, gamma, sigma):
        S, E, I, R = y
        dSdt = -beta * S * I / N
        dEdt = beta * S * I / N - sigma * E
        dIdt = sigma * E - gamma * I
        dRdt = gamma * I
        return dSdt, dEdt, dIdt, dRdt

    # Se carga el vector de condiciones iniciales
    y0 = S0, E0, I0, Rec0

    # Se intengran las ecuaciones del modelo SEIR sobre el vector del espacio temporal.
    ret = odeint(deriv, y0, t, args=(N, beta, gamma, sigma))
    S, E, I, R = ret.T

    # Se crea un nuevo DataFrame con los resultados de la proyección de 180 días
    df = pd.DataFrame({'Localidad':e, 'Susceptibles':S, 'Expuestos': E, 'Infectados':I, 'Recuperados':R})
    df.index.names = ['Dia desde primer caso']

    data = data.append(df)

    # Se guarda el DataFrame del municipio en un archivo separado
    #df.to_csv('Localidad '+str(e)+'.csv')

# Armo una tabla dinámica con la cantidad de infectados proyectada por localidad
infectados = pd.pivot_table(data, index=['Dia desde primer caso'],
                     columns=["Localidad"], values = ['Infectados'], aggfunc=np.sum)

recuperados = pd.pivot_table(data, index=['Dia desde primer caso'],
                     columns=["Localidad"], values = ['Recuperados'], aggfunc=np.sum)

expuestos = pd.pivot_table(data, index=['Dia desde primer caso'],
                     columns=["Localidad"], values = ['Expuestos'], aggfunc=np.sum)

# Crea un excel
writer = ExcelWriter('COVID-19 por localidad.xlsx')

# Graba las tablas dinámicas en una hoja específica del archivo excel
infectados.to_excel(writer, 'Infectados')
recuperados.to_excel(writer, 'Recuperados')
expuestos.to_excel(writer, 'Expuestos')
writer.save()
