from numerapi import NumerAPI, utils

class CustomNumerAPI(NumerAPI):
    def __init__(self):
        super(CustomNumerAPI, self).__init__()
        self.round_performances = {}

    def get_round_performances(self, username):
        if not self.round_performances.get(username):
            query = """
            query($modelName: String!) {
                v3UserProfile(modelName: $modelName) {
                    roundModelPerformances {
                        roundNumber,
                        corr,
                        mmc,
                        mmcMultiplier,
                        roundResolved,
                        roundPayoutFactor
                    }
                }
            }
            """
            arguments = {'modelName': username}
            data = self.raw_query(query, arguments)['data']['v3UserProfile']
            performances = data['roundModelPerformances']
            # convert strings to python objects
            for perf in performances:
                utils.replace(perf, "date", utils.parse_datetime_string)
            # remove useless items
            performances = [p for p in performances if any(list(p.values()))]
            for i in range(len(performances)):
                # for some reason payout factor defaults to object, guessing this is a bug in numerapi
                performances[i]['roundPayoutFactor'] = float(performances[i]['roundPayoutFactor'])
            self.round_performances[username] = performances
        return self.round_performances[username]