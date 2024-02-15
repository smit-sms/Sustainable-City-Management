import csv
from energy_usage.models import SA_energy_consumption

def run():
    fhand = open('energy_usage/data/Dublin_energy_use_poly.csv')
    reader = csv.reader(fhand)
    next(reader) # skip the 1st row

    # Empty the tables to repopulate them.
    SA_energy_consumption.objects.all().delete()

#  ,Dublin City Small Area Code,Estimated Total Annual Energy Use (kWh),Estimated Total Annual Cost of Energy,Total Floor Area,CSO_LEA,geometry
# 0,268139005,827200,92457,3706,NORTH INNER CITY,"MULTIPOLYGON (((-6.269330683999954 53.34993843600006, -6.269421382999951 53.34992618000007, -6.269448422999972 53.34992241900005, -6.269448302999933 53.34992204900004, -6.269628520999959 53.34989699700003, -6.269702389999964 53.34988672600008, -6.269718538999939 53.34988447900008, -6.269769507999968 53.34987925000007, -6.26984859199996 53.34986819100004, -6.269865025999934 53.34986593100007, -6.26994923899997 53.34985432600007, -6.269991008999966 53.34984848700003, -6.270022633999929 53.349842789000036, -6.270040187999939 53.349840347000054, -6.270074478999959 53.34983521800007, -6.270102623999946 53.34983161700006, -6.270119751999971 53.34983078700003, -6.27024156799996 53.34981311200005, -6.270252079999977 53.34981243700008, -6.270332693999933 53.34980107600006, -6.270453564999968 53.349784484000054, -6.270453570999962 53.349785077000035, -6.270454914999959 53.34978489900004, -6.270583623999926 53.34977618500005, -6.270552357999975 53.350060556000074, -6.270540695999955 53.350317447000066, -6.270540790999974 53.35051620200005, -6.27054583499995 53.35071329400006, -6.270471215999976 53.350760586000035, -6.270388422999929 53.35081573200006, -6.270372376999944 53.350827679000076, -6.27031472699997 53.35086989600006, -6.270187761999978 53.35097162500006, -6.270069760999945 53.35101592400008, -6.27003665899997 53.351000569000064, -6.269978800999979 53.35097373600007, -6.269867640999962 53.35092218700004, -6.26985394899998 53.350887510000064, -6.269846033999954 53.350867451000056, -6.269828735999965 53.350817945000074, -6.269784081999944 53.35067651700007, -6.269752077999954 53.35059662500004, -6.269734335999942 53.350569592000056, -6.26970053499997 53.35051810400006, -6.269680082999969 53.350496056000054, -6.269466309999927 53.35026549400004, -6.269450245999963 53.35020520200004, -6.269446491999929 53.35019109000007, -6.269434916999955 53.35016644800004, -6.269344813999965 53.349974504000045, -6.269330683999954 53.34993843600006)))"
# 1,268139006,707019,81314,3595,NORTH INNER CITY,"MULTIPOLYGON (((-6.269211272999939 53.349630138000066, -6.269156923999958 53.34949080700005, -6.269488797999941 53.34940704300004, -6.269787334999933 53.349336366000045, -6.26979655599996 53.349334182000064, -6.26985347599998 53.34932070700006, -6.26986993099996 53.34931681100005, -6.270332584999949 53.34920127200007, -6.270526740999969 53.34914907000007, -6.270579170999952 53.34913369700007, -6.270580905999964 53.34923258200007, -6.27060417399997 53.34927485800006, -6.27060264399995 53.349347900000055, -6.270592585999964 53.34969467700006, -6.270583623999926 53.34977618500005, -6.270454914999959 53.34978489900004, -6.270453570999962 53.349785077000035, -6.270453564999968 53.349784484000054, -6.270332693999933 53.34980107600006, -6.270252079999977 53.34981243700008, -6.27024156799996 53.34981311200005, -6.270119751999971 53.34983078700003, -6.270102623999946 53.34983161700006, -6.270074478999959 53.34983521800007, -6.270040187999939 53.349840347000054, -6.270022633999929 53.349842789000036, -6.269991008999966 53.34984848700003, -6.26994923899997 53.34985432600007, -6.269865025999934 53.34986593100007, -6.26984859199996 53.34986819100004, -6.269769507999968 53.34987925000007, -6.269718538999939 53.34988447900008, -6.269702389999964 53.34988672600008, -6.269628520999959 53.34989699700003, -6.269448302999933 53.34992204900004, -6.269448422999972 53.34992241900005, -6.269421382999951 53.34992618000007, -6.269330683999954 53.34993843600006, -6.269215610999936 53.34964468100003, -6.269211272999939 53.349630138000066)))"
# 2,268139004,1052962,118833,5608,NORTH INNER CITY,"MULTIPOLYGON (((-6.266759151999963 53.352062782000075, -6.266826023999954 53.35202479000003, -6.266867433999948 53.35200124900007, -6.267306843999961 53.351751569000044, -6.266897133999976 53.35152136600004, -6.267156021999938 53.35135764200004, -6.267192853999973 53.35133434900007, -6.26789503699996 53.35164905200003, -6.26825649999995 53.351778901000046, -6.268793628999958 53.35194441900006, -6.268992751999974 53.352005775000066, -6.269052543999976 53.35202420500008, -6.269167988999925 53.352059774000054, -6.269152001999942 53.35208098800007, -6.269074624999973 53.35218363300004, -6.269064064999952 53.35219733900004, -6.269037203999972 53.35223222800005, -6.268900996999946 53.35240909700008, -6.268791781999937 53.352543386000036, -6.268752673999927 53.35258686900005, -6.268701352999926 53.35263629600007, -6.268426211999952 53.35287074800004, -6.268347698999946 53.352923528000076, -6.266759151999963 53.352062782000075)))"

    for row in reader:
        print(row[0],"  ",row[1])
        data_row = SA_energy_consumption(SA_code=row[1], Energy_use=row[2], Energy_cost=row[3], Total_Floor_Area=row[4], Small_Area_Name=row[5])
        data_row.save()