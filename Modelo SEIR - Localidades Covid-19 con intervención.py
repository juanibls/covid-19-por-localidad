
# coding: utf-8

# In[21]:


# Este script está adaptado en base a https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/
# El modelo SEIR se puede consultar en https://belenus.unirioja.es/~jvarona/coronavirus/SEIR-coronavirus.pdf

import numpy as np
from scipy.integrate import odeint
import pandas as pd
from pandas import ExcelWriter

df1 = pd.read_excel('Localidades SEIR.xlsx') 

# Armamos un dataframe vacío donde pondremos todos los resultados
data = pd.DataFrame()

# Se arman listas con los vectores que componen el DataFrame
escenario = df1.Escenario
ini = df1.Inicial
gamma = df1.Gamma
sigma = df1.Sigma
beta1 = df1.Beta1
beta_medidas = df1.Beta_medidas
pob = df1.Poblacion
dias = df1.Dias
inicio_medidas = df1.Inicio_medidas
duracion_medidas = df1.Duracion_medidas

# Se construyen un elemento a partir de una función zip para iterar los 5 parámetros juntos en un bucle
zipped = zip(pob, ini, gamma, beta1, escenario, sigma, beta_medidas, dias, inicio_medidas, duracion_medidas)

# Se arma la iteración para proyectar la curva de cada municipio con sus propios parámetros
for pob,ini,gamma,beta1,escenario,sigma,beta_medidas,dias,inicio_medidas,duracion_medidas in zipped:

    # Pobliación del municipio a partir del elemento "a" de zipped (pob).
    N = pob
    
    # Armamos un vector temporal para proyectar 180 días, con frecuencia diaria
    t = np.linspace(0, dias, dias, dtype = "int")
    
    # Número inicial de contagios en el momento cero a partir del elemento "b" de zipped (ini)
    # Suponemos que el elemento Rec de recuperado en el primer día es 0.
    # Suponemos que los expuestos en el primer día es el producto de contagios y el índice de reproducción (R0 o beta/gamma)
    I0, Rec0, E0 = ini, beta1/gamma, 0

    # Por diferencia calculamos la población Posible que es la diferencia entre la total, la expuesta, la contagiada y la recuperada.
    S0 = N - E0 - I0 - Rec0

    # Se crea una función para resolver el modelo SIR de ecuaciones diferenciales 
    # Para más detalle ver https://belenus.unirioja.es/~jvarona/coronavirus/SEIR-coronavirus.pdf
    def deriv(y, t, N, beta_medidas, beta1, inicio_medidas, duracion_medidas, gamma, sigma):
        S, E, I, R = y
        
        # Redefinimos beta como una función discontinua
        beta = beta_medidas if inicio_medidas+duracion_medidas>= t >=inicio_medidas-1  else beta1
        
        dSdt = -beta * S * I / N
        dEdt = beta * S * I / N - sigma * E
        dIdt = sigma * E - gamma * I
        dRdt = gamma * I
        return dSdt, dEdt, dIdt, dRdt

    # Se carga el vector de condiciones iniciales
    y0 = S0, E0, I0, Rec0

    # Se intengran las ecuaciones del modelo SEIR sobre el vector del espacio temporal.
    ret = odeint(deriv, y0, t, args=(N, beta_medidas, beta1, inicio_medidas, duracion_medidas, gamma, sigma))
    S, E, I, R = ret.T
    
    # Se crea un nuevo DataFrame con los resultados de la proyección de 180 días
    df = pd.DataFrame({'Escenario':escenario, 'Susceptibles':S, 'Expuestos': E, 'Infectados':I, 'Recuperados':R})
    df.index.names = ['Dia desde primer caso']
    
    data = data.append(df)
    
    # Se guarda el DataFrame del municipio en un archivo separado
    #df.to_csv('Localidad '+str(e)+'.csv')

# Armo una tabla dinámica con la cantidad de infectados proyectada por localidad
infectados = pd.pivot_table(data, index=['Dia desde primer caso'], 
                     columns=["Escenario"], values = ['Infectados'], aggfunc=np.sum)

recuperados = pd.pivot_table(data, index=['Dia desde primer caso'], 
                     columns=["Escenario"], values = ['Recuperados'], aggfunc=np.sum)

expuestos = pd.pivot_table(data, index=['Dia desde primer caso'], 
                     columns=["Escenario"], values = ['Expuestos'], aggfunc=np.sum)

# Crea un excel
writer = ExcelWriter('COVID-19 por localidad.xlsx')

# Graba las tablas dinámicas en una hoja específica del archivo excel
infectados.to_excel(writer, 'Infectados')
recuperados.to_excel(writer, 'Recuperados')
expuestos.to_excel(writer, 'Expuestos')
writer.save()

