# Proyección epidemiológica de Covid-19 por localidades
Este script de Python calcula la proyección para n-próximos días de susceptibles, expuestos, infectados y recuperados del Covid-19 de acuerdo con el Modelo epidemiológico SEIR que resulta de una adaptación del Modelo SIR (Kermack y McKendrik, 1927), el cual incorpora la población de expuestos como aquellos que están incuvando el virus pero aún no se presentan como contagiosos.

### Simulación espacial del modelo SEIR, suponiendo que cada persona puede infectar a 8 vecinos inmediatos
![SIR_model_simulated_using_python](https://user-images.githubusercontent.com/20490811/77556419-4251de00-6e97-11ea-92b2-2d85a731cb45.gif)

De acuerdo con este modelo la población de **Susceptibles** pueden infectarse al estar en contacto con alguien de la población de **Infectados**, en base a un parámetro β (beta) denominado "tasa de infección", que dependerá de cuán contagioso sea el virus y representa el promedio de contactos de cada persona por día multiplicado por la probabilidad de transmitir el virus en un contacto entre un infectado y una persona susceptible de ser contagiada. De esta manera, este parámetro puede ser modificado por la acción de políticas de aislamiento social. Por otro lado, los **Infectados** se recuperan con el tiempo, con un parámetro γ (gamma) denominado "tasa de recuperación" y que es la inversa de la cantidad de días que en promedio dura la enfermedad. Una vez que se recuperan se supone que los individuos son inmunes y ya no vuelven a ser susceptibles formando parte de la población de **Recuperados**. Tanto estos últimos como quienes mueren a causa de la enfermedad ya no pueden afectar al desarrollo de la epidemia. 

Este script es una adaptación en base a https://scipython.com/book/chapter-8-scipy/additional-examples/the-sir-epidemic-model/, para el cual se utiliza el modelo SEIR que se puede consultar en https://belenus.unirioja.es/~jvarona/coronavirus/SEIR-coronavirus.pdf

El script toma los parámetros de un archivo Excel llamado *Localidades SEIR.xlsx* en el cual se carga la información específica de cada localidad. De forma alternativa, también se pueden cargar diferentes parámetros de ratio de contagio para una misma localidad como variable de control de la política pública para ver efectos sobre el aplanamiento de la curva de diferentes alternativas de política de aislamiento social.

### Archivo *Localidades SEIR.xlsx*
![localidades-import](https://user-images.githubusercontent.com/20490811/77479853-56e29780-6dff-11ea-814b-d8d9700cad0b.JPG)

El archivo de excel tiene las siguientes columnas:

- Nombre: de la localidad, municipio, provincia, pais. 
- Población total: de la localidad, municipio, provincia o pais.
- Infectados en día cero: debe ser un número mayor a 0.
- Coeficiente beta: ratio de contagio, tal que 1/beta mide la probabilidad de que un susceptible se infecte cuando entra en contacto con un infectado. 
- Coeficiente gamma: ratio de recuperación, 1/gamma es la cantidad de días que se tarda en promedio la recuperación.
- Coeficiente sigma: ratio de incubación, 1/sigma es el tiempo promedio de incubación.
- R0: índice de reproducción del virus, es la relación beta/gamma, representa el número de nuevos infectados producidos por un infectado si toda la población es susceptible.

***
#### Advertencia importante: el modelo es muy sensible a los valores que se les asignan a sus parámetros, en particular al coeficiente R0 (índice de reproducción del virus). Por ejemplo, considerando valores de 1,6 (simil medidas efectivas de aislamientos social) a 4 (simil escenario sin políticas preventivas), las curvas de evolución de infectados pueden alterarse notablemente. 
#### Simulaciones de sensibilidad de infectados a cambios en el índice de reproducción del virus
![r0](https://user-images.githubusercontent.com/20490811/77571314-e8a7de80-6eab-11ea-8027-a89d0d286651.JPG widht='100')
***

Ese archivo es levantado por el script de Python que utiliza estos parámetros y las condiciones iniciales para resolver un sistema de 4 ecuaciones diferenciales simultáneas que captan la trayectoria de cada una de las curvas de **Susceptibles, Expuestos, Infectados y Recuperados** de forma tal que la sumatoria de la población que integra cada uno estos grupos da por resultado la población total.

### Ecuaciones del modelo SEIR
![ecuaciones](https://user-images.githubusercontent.com/20490811/77480037-b2148a00-6dff-11ea-90de-99ea4d89e316.JPG)

Como resultado de la resolución del sistema de ecuaciones diferencuales se devuelve otro archivo excel con la proyección de n-días (en el código está por defecto 180 días) para cada localidad / municipio / provincia / país. El archivo de salida *COVID-19 por localidad.xlsx* cuenta con 3 hojas con la proyección de expuestos, infectados y recuperados respectivamente.

### Resultado de la proyección
![localidades-export](https://user-images.githubusercontent.com/20490811/77480167-f869e900-6dff-11ea-9900-d926e80f7939.JPG)

Contacto Twitter: @juanibalasini
