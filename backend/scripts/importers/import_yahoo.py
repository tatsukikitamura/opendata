# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup

import argparse
import urllib.parse

def main():
    parser = argparse.ArgumentParser(description='Yahoo Transit Scraper')
    parser.add_argument('from_station', help='Departure station')
    parser.add_argument('to_station', help='Destination station')
    parser.add_argument('--via', action='append', help='Via stations (can be used multiple times)')
    args = parser.parse_args()

    departure_station = args.from_station
    destination_station = args.to_station
    
    # URL Encoding
    from_enc = urllib.parse.quote(departure_station)
    to_enc = urllib.parse.quote(destination_station)
    
    # Base URL
    route_url = f"https://transit.yahoo.co.jp/search/print?from={from_enc}&to={to_enc}"
    
    # Add Via Points
    if args.via:
        for v in args.via:
            v_enc = urllib.parse.quote(v)
            route_url += f"&via={v_enc}"

    print(f"Requesting: {route_url}")
    # Requestsを利用してWebページを取得する
    route_response = requests.get(route_url)

    # BeautifulSoupを利用してWebページを解析する
    route_soup = BeautifulSoup(route_response.text, 'html.parser')

    # 経路のサマリーを取得
    route_summary = route_soup.find("div",class_ = "routeSummary")
    
    if not route_summary:
        print("Error: Could not find route summary immediately. Verification needed.")
        # Sometimes Yahoo returns intermediate page or error
        return

    # 所要時間を取得
    required_time = route_summary.find("li",class_ = "time").get_text()
    # 乗り換え回数を取得
    transfer_count = route_summary.find("li", class_ = "transfer").get_text()
    # 料金を取得
    fare = route_summary.find("li", class_ = "fare").get_text()

    print("======"+departure_station+"から"+destination_station+"=======")
    print("所要時間："+required_time)
    print(transfer_count)
    print("料金："+fare)

    # 乗り換えの詳細情報を取得
    route_detail = route_soup.find("div",class_ = "routeDetail")

    # 乗換駅の取得
    stations = []
    stations_tmp = route_detail.find_all("div", class_="station")
    for station in stations_tmp:
        stations.append(station.get_text().strip())

    # 乗り換え路線の取得
    lines = []
    lines_tmp = route_detail.find_all("li", class_="transport")
    for line in lines_tmp:
        line = line.find("div").get_text().strip()
        lines.append(line)

    # 路線ごとの所要時間を取得
    estimated_times = []
    estimated_times_tmp = route_detail.find_all("li", class_="estimatedTime")
    for estimated_time in estimated_times_tmp:
        estimated_times.append(estimated_time.get_text())

    print(estimated_times)

    # 路線ごとの料金を取得
    fars = []
    fars_tmp = route_detail.find_all("p", class_="fare")
    for fare in fars_tmp:
        fars.append(fare.get_text().strip())


    # 乗り換え詳細情報の出力
    print("======乗り換え情報======")
    for station,line,estimated_time,fare in zip(stations,lines,estimated_times,fars):
        print(station)
        print( " | " + line + " " + estimated_time + " " + fare)

    if len(stations) > 0:
        print(stations[len(stations)-1])

if __name__ == "__main__":
    main()
