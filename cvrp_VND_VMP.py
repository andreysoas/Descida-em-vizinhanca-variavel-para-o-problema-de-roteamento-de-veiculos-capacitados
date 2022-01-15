# -*- coding: utf-8 -*-
'''
Solução ótima:
A-n32-k5
solX = [[2, [1, 22, 32, 20, 18, 14, 8, 27]],
      [28, [1, 13, 2, 17, 31]],
      [56, [1, 28, 25]],
      [2, [1, 30, 19, 9, 10, 23, 16, 11, 26, 6, 21]],
      [2, [1, 15, 29, 12, 5, 24, 4, 3, 7]]]

'''

"""#Recebimento e manipulação do arquivo VRP"""

import numpy as np
import itertools
import numpy.random as rd
from math import sqrt
from random import sample
from copy import deepcopy
from math import floor
import time
rd.seed(seed=42)

def cvrpSolution(path:str):
  ''' 
  parâmetros e variáveis do problema
  '''
  demandas = []
  coordenadas = []
  capacidade = None
  startPoint = None
  qtdEntidades = None #receber na entrada
  qtdVeiculos = None #None  #receber na entrada
  currentMin = 999999
  opt = None
  numIter = 20

  '''
  carregando parâmetros, obtendo solução inicial e calculando seu valor
  '''

  capacidade,startPoint,qtdEntidades,qtdVeiculos,opt = carregarDados(path,demandas,coordenadas,startPoint)

  matrizAdj = distMatriz(coordenadas,qtdEntidades)

  solAtual = solbyGuloso(qtdEntidades,capacidade,startPoint,qtdVeiculos,matrizAdj,demandas) #usando solução gulosa
  
  currentMin = solValue(solAtual, matrizAdj,capacidade)
  
  print('Solucao Inicial: ',solAtual)
  print('Valor de solução: ',currentMin)

  '''
  fase de iteração do algoritmo. VND é aplicado por um total de iterações
  definido no programa, ou até que não haja melhoramento da solução corrente
  '''

  min = currentMin 

  for i in range(numIter):
    currentMin=VND(solAtual,currentMin,matrizAdj,capacidade,qtdVeiculos,demandas)

    if min == currentMin: break
    min = currentMin

    print('->',solAtual,' | ',currentMin)
  
  return solAtual,currentMin,opt

def carregarDados(path:str,demandas,coordenadas,startPoint):

  arq = open(path,'r')

  takeNodes = False
  takeDemands = False
  takeDepot = False
  contEntidades = None
  contVehicles = None
  optimal = None
  capacidade = None

  section = 1

  for line in arq:

    
    if section == 2:

      if takeNodes: #--------------------

        if len(coordenadas) == contEntidades:
          takeNodes = False
          takeDemands = True
        else:
          seps = line.split(' ')
          coordenadas.append([int(seps[1]),int(seps[2]),int(seps[3][:-1])])


      elif takeDemands: #----------------

        if len(demandas) == contEntidades:
          takeDemands = False
          takeDepot = True

        else:
          demandas.append(int(line.split(' ')[1][:]))


      elif takeDepot: #------------------

        startPoint = int(line[1:-1])

        takeDepot = False

        section+=1


    
    if section == 1:

      if 'COMMENT' in line:
        seps = line.split(': ')
        contVehicles = int(seps[2].split(',')[0])
        optimal = int(seps[3][:-2]) #\n
      
      elif 'DIMENSION' in line:
        contEntidades = int(line.split(': ')[1][:-1])
      
      elif 'CAPACITY' in line:
        capacidade = int(line.split(': ')[1][:-1])
      
      elif 'NODE' in line:
        takeNodes = True
        section+=1



  arq.close()

  return capacidade,startPoint,contEntidades,contVehicles,optimal

"""Construir a matriz de distâncias"""

def distMatriz(coordenadas,qtdEntidades):
  
  matrizAdj = np.ones((qtdEntidades,qtdEntidades))
  m = 0

  for i in coordenadas:
    n=0
    for j in coordenadas:
      if m!=n:
        matrizAdj[m][n] = round(sqrt((i[2]-j[2])**2 + (i[1]-j[1])**2))
      else:
        matrizAdj[m][n] = 9999
      n+=1
    m+=1

  return matrizAdj

"""#Desenvolvimento do algoritmo

Cálculo do valor da solução
"""

def solValue(solucao:list,matrizAdj:np.ndarray,capacidade:int): #considerando solução vazia
  valor = 0

  for i in solucao:
    valor+=calcOneroute(i[1],matrizAdj)
    
  return valor

def calcOneroute(route,matrizAdj):
  valor = 0
  
  for i in range(1,len(route)):
    valor += matrizAdj[route[i-1]-1][route[i]-1]
  valor+=matrizAdj[route[-1]-1][0]
  
  return valor

"""#VND"""

def N1(solAtual:list,qtdVeiculos:int,capacidade:int,matrizAdj):

  solOpt = [] #vai armazenar os pares(índices)que geraram a mudança: diminuição no valor da solução
  melhorou = False
  newSol = deepcopy(solAtual)


  for i in range(qtdVeiculos):

    rota = [i,None,None,0]

    if len(newSol[i][1]) >= 3:
      valor1 = calcOneroute(newSol[i][1],matrizAdj)
      for j in range(1,len(newSol[i][1])):
        for k in range(j+1,len(newSol[i][1])):

          newSol[i][1][j],newSol[i][1][k] = newSol[i][1][k],newSol[i][1][j]

          valor2 = calcOneroute(newSol[i][1],matrizAdj)
          newSol[i][1][j],newSol[i][1][k] = newSol[i][1][k],newSol[i][1][j]
          #print('valor1: ',valor1)
          #print('valor2: ',valor2)
          if valor2 < valor1:                               #se houve melhora
            dif = valor2 - valor1
            
            if dif < rota[3]:
              rota[1] = j
              rota[2] = k
              rota[3] = dif
              melhorou = True

    if rota[3] < 0:
      solOpt.append(rota)
 
  for i in solOpt:
    solAtual[i[0]][1][i[1]],solAtual[i[0]][1][i[2]] = solAtual[i[0]][1][i[2]],solAtual[i[0]][1][i[1]]
  #print(solOpt)
  return melhorou

def N2(solAtual:list,qtdVeiculos:int,capacidade:int,matrizAdj,demandas,atualMin): # kn^2
 
  solOpt = [deepcopy(solAtual)]
  newSol = deepcopy(solAtual)
  melhorou = False


  for i in range(qtdVeiculos-1):
      for j in range(1,len(newSol[i][1])):
        for m in range(i+1,qtdVeiculos):
          for n in range(1,len(newSol[m][1])):  #j e n

            capacidade1 = newSol[i][0] + demandas[newSol[i][1][j]-1] - demandas[newSol[m][1][n]-1]
            capacidade2 = newSol[m][0] + demandas[newSol[m][1][n]-1] - demandas[newSol[i][1][j]-1]
                                                                          #checagem da viabilidade da alteração
            if capacidade1>=0 and capacidade2>=0:

              newSol[m][1][n],newSol[i][1][j] = newSol[i][1][j],newSol[m][1][n]

              newSol[i][0],capacidade1 = capacidade1,newSol[i][0]
              newSol[m][0],capacidade2 = capacidade2,newSol[m][0]
                                                                          #Checagem para decidir se a alteração diminui o valor da solução
              valor = solValue(newSol,matrizAdj,capacidade)

              if valor < atualMin: #atual Mínimo
                solOpt[0] = deepcopy(newSol)
                atualMin = valor
                melhorou = True

              newSol[m][1][n],newSol[i][1][j] = newSol[i][1][j],newSol[m][1][n]
              newSol[i][0] = capacidade1
              newSol[m][0] = capacidade2

  for i in range(qtdVeiculos):
    solAtual[i][0] = solOpt[0][i][0]
    for j in range(len(solAtual[i][1])):
      solAtual[i][1][j] = solOpt[0][i][1][j]

  return melhorou

def N3(solAtual,qtdVeiculos,matrizAdj,currentMin):
  newSol = deepcopy(solAtual)
  changes = []
  melhorou = False

  for i in range(qtdVeiculos):
    K = len(newSol[i][1])

    if K>=4:
      
      route = newSol[i][1][:]
      for j in range(1,floor(K/2)):
        route[j],route[-j] = route[-j],route[j]

      valor1 = calcOneroute(newSol[i][1],matrizAdj)
      valor2 = calcOneroute(route,matrizAdj)

      if valor2<valor1:
        changes.append((i,route))
        melhorou = True

  for i in changes:
    solAtual[i[0]][1] = i[1]

  return melhorou

# troca dois a dois na sequência

def N4(solAtual:list,matrizAdj,qtdVeiculos):
  newSol = deepcopy(solAtual)
  melhorou = False
  changes = []

  for i in range(qtdVeiculos):
    tamRota = len(newSol[i][1])
    if tamRota >=3:
      valor1 = calcOneroute(newSol[i][1],matrizAdj)

      doisAdois_laco(newSol[i][1],tamRota)
      
      valor2 = calcOneroute(newSol[i][1],matrizAdj)

      if valor2 < valor1:
        melhorou = True
        doisAdois_laco(solAtual[i][1],tamRota)
  
  return melhorou


def doisAdois_laco(route,tamRota):
  for j in range(2,tamRota,2): #2 steps
    route[j],route[j-1] = route[j-1],route[j]

def VND(solAtual:list,currentMin,matrizAdj,capacidade,qtdVeiculos,demandas): # ( Usando cyclic neighborhood change step)

  atualMin = currentMin

  N1(solAtual,qtdVeiculos,capacidade,matrizAdj)
  atualMin = solValue(solAtual,matrizAdj,capacidade)

  N2(solAtual,qtdVeiculos,capacidade,matrizAdj,demandas,currentMin)
  atualMin = solValue(solAtual,matrizAdj,capacidade)

  N3(solAtual,qtdVeiculos,matrizAdj,currentMin)
  atualMin = solValue(solAtual,matrizAdj,capacidade)

  N4(solAtual,matrizAdj,qtdVeiculos)
  atualMin = solValue(solAtual,matrizAdj,capacidade)

  return atualMin

"""#Método guloso

Ideia: gerar uma rota de custo mínimo para um veículo, onde o novo ponto adicionado é tal que 
a distância mínima do atual último na rota até este é a menor dentre os pontos disponíveis.

os pontos são adicionados à rota de um veículo até que as demandas dos pontos disponíveis 
não ultrapassem a capacidade suportada pelo veículo.

Heurística do vizinho mais próximo. (VMP)
"""

def solbyGuloso(qtdEntidades,capacidade,startPoint,qtdVeiculos,matrizAdj,demandas):

  entidades = np.arange(1,qtdEntidades+1,dtype=int)

  solInicial = [[capacidade,[]] for i in range(qtdVeiculos)]
  
  setDisponiveis = [i for i in range(1,qtdEntidades+1)]
  setDisponiveis.remove(startPoint)
  tamSet = qtdEntidades

  for i in range(qtdVeiculos):
    setDisponiveis.append(startPoint)
    VMP(startPoint,solInicial[i],matrizAdj,setDisponiveis,demandas)
  
  return solInicial

def VMP(atualV,route,matrizAdj,setDisponiveis,demandas):
 
  route[0] -= demandas[atualV-1]
  route[1].append(atualV)
  setDisponiveis.remove(atualV)

  min = [-1,99999]
  change = False

  for i in setDisponiveis:
    if demandas[i-1] <= route[0]:
      if matrizAdj[atualV-1][i-1] < min[1]:
        min[1] = matrizAdj[atualV-1][i-1]
        min[0] = i
        change = True

  if not change: return

  VMP(min[0],route,matrizAdj,setDisponiveis,demandas)

def main():
  
  path = input('path do arquivo txt: ')
  
  try:
    ini = time.time()
    result = cvrpSolution(path)
    fim = time.time()
  except FileNotFoundError:
    print('Diretório incorreto!')
    return
  
  print('tempo( em segundos ): ',fim-ini)
  print('Desvio com relação ao ótimo: ',round(((result[1] - result[2])/result[2]),4)*100,'%')

  return

if __name__ == '__main__':
  main()
