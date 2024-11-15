from django.shortcuts import render
from .models import Festival, TravelDestination

def festival_list(request):
    # 모든 축제 정보를 가져옵니다.
    festivals = Festival.objects.all()
    # 축제의 총 개수를 계산합니다.
    festival_count = festivals.count()
    
    # 템플릿에 전달할 데이터
    context = {
        'festivals': festivals,
        'festival_count': festival_count
    }
    return render(request, 'places/festival_list.html', context)

def travel_destination_list(request):
    destinations = TravelDestination.objects.all()
    destination_count = destinations.count()
    return render(request, 'places/travel_list.html', {
        'destinations': destinations,
        'destination_count': destination_count
    })
