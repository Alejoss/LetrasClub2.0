# -*- coding: utf-8 -*-
import json
import csv
import requests

archivo = raw_input("Nombre del Archivo csv (completo): ")
bcompartida = raw_input("Nombre de la biblioteca compartida (exacto): ")

archivo = "archivo_libros/"+archivo

with open(archivo, 'rb') as archivo_csv:
    csv_reader = csv.reader(archivo_csv)

    diccionario_enviar = {
        'libros_json': {
            'biblioteca_compartida_nombre': bcompartida,
            'libros': {
            }
        }
    }

    contador = 0
    for row in csv_reader:
        contador += 1
        autor = row[0]
        titulo = row[1]
        descripcion = row[2]
        if descripcion == "-":
            descripcion = ""

        diccionario_enviar['libros_json']['libros'][contador] = {
            'titulo': titulo,
            'autor': autor,
            'descripcion': descripcion
        }

    # http://www.letras.club/libros/crear_libros_bcompartida/
    respuesta = requests.post("http://localhost:8000/libros/crear_libros_bcompartida/", json=(diccionario_enviar))

    print respuesta
    for l in json.loads(respuesta.content):
        print "-------------------------------------------------------".join(l)
