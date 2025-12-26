from django.core.management.base import BaseCommand
from api.models import Destination, TrekRoute, ChatRoom


class Command(BaseCommand):
    help = 'Load sample trekking destinations and routes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample destinations...')
        
        # Annapurna Base Camp
        abc = Destination.objects.create(
            name='Annapurna Base Camp Trek',
            description='Experience the magnificent Annapurna massif up close. This trek takes you through diverse landscapes, from lush rhododendron forests to high alpine terrain, culminating at the base camp surrounded by towering peaks.',
            location='Annapurna Region, Nepal',
            altitude=4130,
            duration_days=7,
            difficulty='MODERATE',
            price=750.00,
            featured=True,
            best_season='March-May, September-November',
            group_size_max=12,
            latitude=28.5310,
            longitude=83.8740
        )
        
        # Create route points for ABC
        abc_route_points = [
            (28.3949, 83.9694, 1400, 'Nayapul', 'Trek starting point'),
            (28.3919, 83.9336, 2870, 'Ghorepani', 'Beautiful village with mountain views'),
            (28.3894, 83.9025, 3210, 'Poon Hill', 'Famous viewpoint for sunrise'),
            (28.4821, 83.8686, 2170, 'Chomrong', 'Large Gurung village'),
            (28.5134, 83.8561, 3230, 'Deurali', 'High altitude stop'),
            (28.5310, 83.8740, 4130, 'Annapurna Base Camp', 'Final destination'),
        ]
        
        for i, (lat, lon, alt, name, desc) in enumerate(abc_route_points, 1):
            TrekRoute.objects.create(
                destination=abc,
                sequence_order=i,
                latitude=lat,
                longitude=lon,
                altitude=alt,
                location_name=name,
                description=desc
            )
        
        # Create chat room for ABC
        ChatRoom.objects.get_or_create(destination=abc)
        
        # Everest Base Camp
        ebc = Destination.objects.create(
            name='Everest Base Camp Trek',
            description='The ultimate trek to the base of the world\'s highest mountain. Journey through Sherpa villages, Buddhist monasteries, and challenging high-altitude terrain to reach the legendary Everest Base Camp.',
            location='Khumbu Region, Nepal',
            altitude=5364,
            duration_days=12,
            difficulty='CHALLENGING',
            price=1250.00,
            featured=True,
            best_season='March-May, September-November',
            group_size_max=10,
            latitude=27.9881,
            longitude=86.9253
        )
        
        # Create route points for EBC
        ebc_route_points = [
            (27.7000, 86.7333, 2860, 'Lukla', 'Gateway to Everest'),
            (27.7397, 86.7147, 3440, 'Namche Bazaar', 'Sherpa capital'),
            (27.8144, 86.7714, 3867, 'Tengboche', 'Famous monastery'),
            (27.9006, 86.8286, 4410, 'Dingboche', 'Acclimatization stop'),
            (27.9519, 86.8614, 5164, 'Lobuche', 'High altitude village'),
            (27.9881, 86.9253, 5364, 'Everest Base Camp', 'Base of Mount Everest'),
        ]
        
        for i, (lat, lon, alt, name, desc) in enumerate(ebc_route_points, 1):
            TrekRoute.objects.create(
                destination=ebc,
                sequence_order=i,
                latitude=lat,
                longitude=lon,
                altitude=alt,
                location_name=name,
                description=desc
            )
        
        ChatRoom.objects.get_or_create(destination=ebc)
        
        # Langtang Valley Trek
        langtang = Destination.objects.create(
            name='Langtang Valley Trek',
            description='Explore the stunning Langtang Valley, known as the "Valley of Glaciers". This trek offers beautiful mountain scenery, diverse wildlife, and authentic Tamang culture.',
            location='Langtang Region, Nepal',
            altitude=3800,
            duration_days=8,
            difficulty='MODERATE',
            price=650.00,
            featured=True,
            best_season='March-May, September-November',
            group_size_max=15,
            latitude=28.2164,
            longitude=85.5500
        )
        
        langtang_route_points = [
            (28.1045, 85.3231, 1460, 'Syabrubesi', 'Trek starting point'),
            (28.1586, 85.4086, 2380, 'Lama Hotel', 'Forest lodge'),
            (28.2000, 85.5000, 3430, 'Langtang Village', 'Main village'),
            (28.2164, 85.5500, 3800, 'Kyanjin Gompa', 'Ancient monastery'),
        ]
        
        for i, (lat, lon, alt, name, desc) in enumerate(langtang_route_points, 1):
            TrekRoute.objects.create(
                destination=langtang,
                sequence_order=i,
                latitude=lat,
                longitude=lon,
                altitude=alt,
                location_name=name,
                description=desc
            )
        
        ChatRoom.objects.get_or_create(destination=langtang)
        
        # Manaslu Circuit Trek
        manaslu = Destination.objects.create(
            name='Manaslu Circuit Trek',
            description='Trek around the eighth highest mountain in the world. This less-crowded alternative to the Annapurna Circuit offers pristine mountain beauty and rich Buddhist culture.',
            location='Manaslu Region, Nepal',
            altitude=5160,
            duration_days=14,
            difficulty='DIFFICULT',
            price=1400.00,
            featured=False,
            best_season='March-May, September-November',
            group_size_max=10,
            latitude=28.5495,
            longitude=84.5595
        )
        
        manaslu_route_points = [
            (28.2847, 84.7231, 700, 'Soti Khola', 'Starting point'),
            (28.4500, 84.6000, 1860, 'Machha Khola', 'Riverside village'),
            (28.5000, 84.5500, 3520, 'Samagaon', 'Tibetan village'),
            (28.5495, 84.5595, 5160, 'Larkya La Pass', 'High mountain pass'),
        ]
        
        for i, (lat, lon, alt, name, desc) in enumerate(manaslu_route_points, 1):
            TrekRoute.objects.create(
                destination=manaslu,
                sequence_order=i,
                latitude=lat,
                longitude=lon,
                altitude=alt,
                location_name=name,
                description=desc
            )
        
        ChatRoom.objects.get_or_create(destination=manaslu)
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample destinations!'))
        self.stdout.write(f'Created {Destination.objects.count()} destinations')
        self.stdout.write(f'Created {TrekRoute.objects.count()} route points')
        self.stdout.write(f'Created {ChatRoom.objects.count()} chat rooms')
